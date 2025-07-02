#!/usr/bin/python3

import json
import time
import csv
import sys
import os
import re
import subprocess
import statistics
from datetime import datetime
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mininet.node import Controller
from mininet.log import setLogLevel, info

class MeshLogger:
    """Sistema de logs estruturado e exportável"""
    
    def __init__(self, output_dir='results'):
        self.output_dir = output_dir
        self.logs = {
            'network_metrics': [],
            'station_metrics': {},
            'handover_events': [],
            'errors': []
        }
        os.makedirs(output_dir, exist_ok=True)
    
    def log_network_metric(self, metric_type, value, timestamp=None):
        """Log de métricas da rede"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.logs['network_metrics'].append({
            'timestamp': timestamp,
            'type': metric_type,
            'value': value
        })
    
    def log_station_metric(self, station_name, position, rssi, latency_data, ap_connected, aps_visible, timestamp=None):
        """Log de métricas de station específica"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        if station_name not in self.logs['station_metrics']:
            self.logs['station_metrics'][station_name] = []
        
        self.logs['station_metrics'][station_name].append({
            'timestamp': timestamp,
            'position': position,
            'rssi': rssi,
            'latency_avg': latency_data.get('latencia_media', 0),
            'latency_jitter': latency_data.get('jitter', 0),
            'packet_loss': latency_data.get('packet_loss', 0),
            'ap_connected': ap_connected,
            'aps_visible': aps_visible
        })
    
    def log_handover_event(self, station_name, from_ap, to_ap, reason, timestamp=None):
        """Log de eventos de handover"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.logs['handover_events'].append({
            'timestamp': timestamp,
            'station': station_name,
            'from_ap': from_ap,
            'to_ap': to_ap,
            'reason': reason
        })
    
    def log_error(self, error_type, message, timestamp=None):
        """Log de erros"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.logs['errors'].append({
            'timestamp': timestamp,
            'type': error_type,
            'message': message
        })
    
    def export_csv(self):
        """Exporta logs em formato CSV"""
        # Exportar métricas de rede
        network_file = os.path.join(self.output_dir, 'network_metrics.csv')
        with open(network_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'type', 'value'])
            writer.writeheader()
            for metric in self.logs['network_metrics']:
                writer.writerow(metric)
        
        # Exportar métricas de stations
        for station_name, metrics in self.logs['station_metrics'].items():
            station_file = os.path.join(self.output_dir, f'{station_name}_metrics.csv')
            with open(station_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'position', 'rssi', 'latency_avg', 
                    'latency_jitter', 'packet_loss', 'ap_connected', 'aps_visible'
                ])
                writer.writeheader()
                for metric in metrics:
                    writer.writerow(metric)
        
        # Exportar eventos de handover
        handover_file = os.path.join(self.output_dir, 'handover_events.csv')
        with open(handover_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'station', 'from_ap', 'to_ap', 'reason'])
            writer.writeheader()
            for event in self.logs['handover_events']:
                writer.writerow(event)
    
    def export_json(self):
        """Exporta logs em formato JSON"""
        json_file = os.path.join(self.output_dir, 'complete_logs.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
    
    def generate_summary(self):
        """Gera resumo dos logs"""
        summary = {
            'total_network_metrics': len(self.logs['network_metrics']),
            'total_stations': len(self.logs['station_metrics']),
            'total_handover_events': len(self.logs['handover_events']),
            'total_errors': len(self.logs['errors']),
            'stations': {}
        }
        
        for station_name, metrics in self.logs['station_metrics'].items():
            if metrics:
                rssi_values = [m['rssi'] for m in metrics if m['rssi'] != -100]
                latency_values = [m['latency_avg'] for m in metrics if m['latency_avg'] > 0]
                
                summary['stations'][station_name] = {
                    'total_measurements': len(metrics),
                    'avg_rssi': statistics.mean(rssi_values) if rssi_values else -100,
                    'avg_latency': statistics.mean(latency_values) if latency_values else 0,
                    'handover_count': len([e for e in self.logs['handover_events'] if e['station'] == station_name])
                }
        
        return summary

def obter_rssi_robusto(sta, sta_name, tentativas=3):
    """Obtém RSSI com múltiplas tentativas e média"""
    rssi_values = []
    
    for i in range(tentativas):
        try:
            # Tentar diferentes comandos para obter RSSI
            cmd1 = f"iw dev {sta_name}-wlan0 link"
            result1 = sta.cmd(cmd1)
            
            for line in result1.split('\n'):
                if 'signal:' in line:
                    match = re.search(r'signal:\s*([-\d]+)', line)
                    if match:
                        rssi = int(match.group(1).strip())
                        if rssi > -100:  # Valor válido
                            rssi_values.append(rssi)
                            break
            
            # Se não encontrou, tentar iwconfig
            if not rssi_values:
                cmd2 = f"iwconfig {sta_name}-wlan0 | grep -i quality"
                result2 = sta.cmd(cmd2)
                for line in result2.split('\n'):
                    if 'signal level' in line.lower():
                        match = re.search(r'signal level[=:]\s*([-\d]+)', line, re.IGNORECASE)
                        if match:
                            rssi = int(match.group(1).strip())
                            if rssi > -100:
                                rssi_values.append(rssi)
                                break
            
            # Pequena pausa entre tentativas
            time.sleep(0.1)
            
        except Exception as e:
            continue
    
    # Retornar média dos valores válidos ou -100 se nenhum válido
    if rssi_values:
        return int(statistics.mean(rssi_values))
    else:
        return -100

def obter_latencia_completa(sta, tentativas=5):
    """Mede latência com jitter e packet loss"""
    latencias = []
    perdidos = 0
    
    for i in range(tentativas):
        try:
            # Ping com timeout menor
            ping_result = sta.cmd('ping -c 1 -W 1 10.0.0.1')
            
            for line in ping_result.split('\n'):
                if 'time=' in line:
                    match = re.search(r'time=([\d.]+)', line)
                    if match:
                        latencia = float(match.group(1))
                        latencias.append(latencia)
                        break
            else:
                # Se não encontrou time=, tentar ping para 8.8.8.8
                ping_result = sta.cmd('ping -c 1 -W 1 8.8.8.8')
                for line in ping_result.split('\n'):
                    if 'time=' in line:
                        match = re.search(r'time=([\d.]+)', line)
                        if match:
                            latencia = float(match.group(1))
                            latencias.append(latencia)
                            break
                else:
                    perdidos += 1
            
            time.sleep(0.1)
            
        except Exception as e:
            perdidos += 1
    
    # Calcular estatísticas
    if latencias:
        latencia_media = statistics.mean(latencias)
        jitter = statistics.stdev(latencias) if len(latencias) > 1 else 0
    else:
        latencia_media = 9999
        jitter = 0
    
    packet_loss = perdidos / tentativas if tentativas > 0 else 1
    
    return {
        'latencia_media': latencia_media,
        'jitter': jitter,
        'packet_loss': packet_loss,
        'tentativas_validas': len(latencias)
    }

def obter_ap_especifico_melhorado(sta, sta_name, ap_objs):
    """Identifica qual AP específico a station está conectada de forma mais robusta"""
    try:
        # Verificar se está conectado
        cmd = f"iw dev {sta_name}-wlan0 link"
        result = sta.cmd(cmd)
        
        if 'Not connected' in result or 'No such device' in result:
            return 'desconectado'
        
        # Tentar ping para cada AP para descobrir qual está respondendo
        for ap_name, ap in ap_objs.items():
            try:
                # Tentar ping para o IP do AP
                ap_ip = f"10.0.0.{list(ap_objs.keys()).index(ap_name) + 1}"
                ping_result = sta.cmd(f'ping -c 1 -W 1 {ap_ip}')
                
                if '1 received' in ping_result or '1 packets received' in ping_result:
                    return ap_name
            except:
                continue
        
        # Se não conseguir identificar, retornar SSID
        for line in result.split('\n'):
            if 'SSID:' in line:
                match = re.search(r'SSID:\s*(\S+)', line)
                if match:
                    return f"SSID:{match.group(1).strip()}"
        
        return 'conectado_desconhecido'
    except Exception as e:
        return 'erro_conexao'

def scan_wifi_melhorado(sta, sta_name):
    """Faz scan Wi-Fi melhorado e retorna APs ordenados por qualidade"""
    try:
        # Fazer scan das redes Wi-Fi
        scan_result = sta.cmd(f'iw dev {sta_name}-wlan0 scan')
        
        aps_visiveis = []
        current_bssid = None
        current_signal = None
        current_ssid = None
        
        for line in scan_result.split('\n'):
            line = line.strip()
            
            # Detectar BSS (Basic Service Set)
            if line.startswith('BSS '):
                current_bssid = line.split()[1]
                current_signal = None
                current_ssid = None
            
            # Detectar sinal
            elif 'signal:' in line:
                try:
                    signal_part = line.split('signal:')[1].strip()
                    current_signal = int(float(signal_part.split()[0]))
                except:
                    current_signal = None
            
            # Detectar SSID
            elif 'SSID:' in line:
                try:
                    ssid_part = line.split('SSID:')[1].strip()
                    if ssid_part and ssid_part != '':
                        current_ssid = ssid_part
                except:
                    current_ssid = None
            
            # Se temos BSS, sinal e SSID, adicionar à lista
            if current_bssid and current_signal is not None and current_ssid:
                aps_visiveis.append({
                    'ssid': current_ssid,
                    'signal': current_signal,
                    'bssid': current_bssid
                })
                current_bssid = None
                current_signal = None
                current_ssid = None
        
        # Ordenar por qualidade de sinal (maior primeiro)
        aps_visiveis.sort(key=lambda x: x['signal'], reverse=True)
        
        # Retornar string formatada
        if aps_visiveis:
            return ';'.join([f"{ap['ssid']}:{ap['signal']}" for ap in aps_visiveis])
        else:
            return 'nenhum_ap_detectado'
        
    except Exception as e:
        return 'erro_scan'

def handover_inteligente(sta, sta_name, ap_objs, logger, threshold_rssi=-50, hysteresis=5):
    """Força handover baseado em RSSI com histerese"""
    try:
        # Obter AP atual
        ap_atual = obter_ap_especifico_melhorado(sta, sta_name, ap_objs)
        
        # Scan de todos os APs
        melhor_ap = None
        melhor_rssi = -100
        
        for ap_name, ap in ap_objs.items():
            try:
                # Tentar obter RSSI específico do AP
                rssi = obter_rssi_robusto(sta, sta_name, tentativas=2)
                
                # Se este AP tem melhor sinal
                if rssi > melhor_rssi:
                    melhor_rssi = rssi
                    melhor_ap = ap_name
                    
            except Exception as e:
                continue
        
        # Decisão de handover com histerese
        if melhor_ap and melhor_ap != ap_atual:
            # Se o melhor AP tem sinal significativamente melhor
            if melhor_rssi > threshold_rssi:
                # Aplicar histerese: só fazer handover se diferença for maior que hysteresis
                if melhor_rssi > threshold_rssi + hysteresis:
                    # Forçar handover
                    try:
                        # Desconectar do AP atual
                        sta.cmd(f"iw dev {sta_name}-wlan0 disconnect")
                        time.sleep(1)
                        
                        # Conectar ao novo AP
                        sta.cmd(f"iw dev {sta_name}-wlan0 connect {melhor_ap}")
                        time.sleep(2)
                        
                        # Log do evento de handover
                        logger.log_handover_event(
                            station_name=sta_name,
                            from_ap=ap_atual,
                            to_ap=melhor_ap,
                            reason=f"RSSI melhor: {melhor_rssi} vs threshold {threshold_rssi}"
                        )
                        
                        return melhor_ap
                        
                    except Exception as e:
                        logger.log_error('handover_failed', f"Erro no handover: {e}")
                        return ap_atual
        
        return ap_atual
        
    except Exception as e:
        logger.log_error('handover_error', f"Erro no handover inteligente: {e}")
        return ap_atual

def carregar_config(arquivo):
    """Carrega configuração do arquivo JSON"""
    with open(arquivo, 'r') as f:
        return json.load(f)

def executar_simulacao_mesh_v3(config):
    """Executa simulação mesh com melhorias implementadas"""
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)
    logger = MeshLogger()

    info("*** Criando APs\n")
    ap_objs = {}
    for ap in config["aps"]:
        # Adicionar parâmetro range se especificado
        ap_params = {
            "name": ap["name"],
            "ssid": config.get("ssid", "meshNet"),
            "mode": "g",
            "channel": str(config.get("channel", 1)),
            "position": f'{ap["x"]},{ap["y"]},0'
        }
        
        # Adicionar range se especificado no JSON
        if "range" in ap:
            ap_params["range"] = ap["range"]
        
        # Adicionar txpower se especificado no JSON
        if "txpower" in ap:
            ap_params["txpower"] = ap["txpower"]
        
        ap_objs[ap["name"]] = net.addAccessPoint(**ap_params)

    info("*** Criando stations\n")
    sta_objs = {}
    for sta in config["stations"]:
        sta_objs[sta["name"]] = net.addStation(
            sta["name"],
            position=f'{sta["start_x"]},{sta["start_y"]},0'
        )

    c1 = net.addController('c1')
    net.configureWifiNodes()

    info("*** Iniciando rede\n")
    net.build()
    c1.start()
    for ap in ap_objs.values():
        ap.start([c1])

    # Aguardar estabilização da rede
    info("*** Aguardando estabilização da rede\n")
    time.sleep(3)

    # Log inicial da rede
    logger.log_network_metric('network_start', {
        'total_aps': len(ap_objs),
        'total_stations': len(sta_objs),
        'ssid': config.get("ssid", "meshNet")
    })

    info("*** Movimentando stations com handover inteligente\n")
    for sta_conf in config["stations"]:
        sta = sta_objs[sta_conf["name"]]
        
        # Log da posição inicial
        rssi = obter_rssi_robusto(sta, sta_conf["name"])
        latency_data = obter_latencia_completa(sta)
        ap_conectado = obter_ap_especifico_melhorado(sta, sta_conf["name"], ap_objs)
        aps_visiveis = scan_wifi_melhorado(sta, sta_conf["name"])
        
        logger.log_station_metric(
            station_name=sta_conf["name"],
            position=f'{sta_conf["start_x"]},{sta_conf["start_y"]}',
            rssi=rssi,
            latency_data=latency_data,
            ap_connected=ap_conectado,
            aps_visible=aps_visiveis
        )
        
        info(f"{sta_conf['name']} → pos=({sta_conf['start_x']},{sta_conf['start_y']}) "
             f"RSSI={rssi} latency={latency_data['latencia_media']:.3f}ms "
             f"jitter={latency_data['jitter']:.3f}ms loss={latency_data['packet_loss']:.1%} "
             f"AP={ap_conectado} Scan={aps_visiveis}\n")

        # Mover pelas trajetórias com handover inteligente
        for i, point in enumerate(sta_conf["trajectory"]):
            x, y = point
            sta.setPosition(f'{x},{y},0')
            time.sleep(config.get("wait", 2))

            # Obter métricas
            rssi = obter_rssi_robusto(sta, sta_conf["name"])
            latency_data = obter_latencia_completa(sta)
            ap_conectado = obter_ap_especifico_melhorado(sta, sta_conf["name"], ap_objs)
            aps_visiveis = scan_wifi_melhorado(sta, sta_conf["name"])

            # Tentar handover inteligente
            ap_apos_handover = handover_inteligente(sta, sta_conf["name"], ap_objs, logger)
            
            # Se houve handover, atualizar métricas
            if ap_apos_handover != ap_conectado:
                rssi = obter_rssi_robusto(sta, sta_conf["name"])
                latency_data = obter_latencia_completa(sta)
                ap_conectado = ap_apos_handover

            logger.log_station_metric(
                station_name=sta_conf["name"],
                position=f'{x},{y}',
                rssi=rssi,
                latency_data=latency_data,
                ap_connected=ap_conectado,
                aps_visible=aps_visiveis
            )
            
            info(f"{sta_conf['name']} → pos=({x},{y}) "
                 f"RSSI={rssi} latency={latency_data['latencia_media']:.3f}ms "
                 f"jitter={latency_data['jitter']:.3f}ms loss={latency_data['packet_loss']:.1%} "
                 f"AP={ap_conectado} Scan={aps_visiveis}\n")

    # Log final da rede
    logger.log_network_metric('network_end', {
        'total_handover_events': len(logger.logs['handover_events']),
        'total_errors': len(logger.logs['errors'])
    })

    # Exportar logs
    logger.export_csv()
    logger.export_json()
    
    # Gerar e mostrar resumo
    summary = logger.generate_summary()
    info(f"\n*** RESUMO DA SIMULAÇÃO ***\n")
    info(f"Total de métricas de rede: {summary['total_network_metrics']}\n")
    info(f"Total de eventos de handover: {summary['total_handover_events']}\n")
    info(f"Total de erros: {summary['total_errors']}\n")
    
    for station_name, stats in summary['stations'].items():
        info(f"{station_name}: {stats['total_measurements']} medições, "
             f"RSSI médio: {stats['avg_rssi']:.1f}, "
             f"Latência média: {stats['avg_latency']:.3f}ms, "
             f"Handovers: {stats['handover_count']}\n")

    info("*** Encerrando rede\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    if len(sys.argv) < 2:
        print("Uso: python3 executa_cenario_mesh_v3.py cenario.json")
        sys.exit(1)
    conf = carregar_config(sys.argv[1])
    executar_simulacao_mesh_v3(conf)
