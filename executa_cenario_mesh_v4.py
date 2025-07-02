#!/usr/bin/env python3
"""
DSL Mininet-WiFi - Versão 4.0 SUPER COMPLETA
Coleta TODAS as informações WiFi possíveis no formato original:
- SSID e BSSID detalhados
- RSSI com qualidade
- Latência com packet loss
- Bandwidth/Throughput (iperf3)
- Handover inteligente
- Scan completo de redes
- Logs no formato original do usuário
"""

import json
import time
import csv
import os
import re
import sys
import statistics
import subprocess
from datetime import datetime
from mininet.log import info, error
from mininet_wifi.net import Mininet_wifi
from mininet_wifi.node import Controller, OVSKernelAP

def obter_info_wifi_detalhada(sta, sta_name):
    """Obtém informações WiFi detalhadas (SSID, BSSID, RSSI)"""
    try:
        cmd = f"iw dev {sta_name}-wlan0 link"
        result = sta.cmd(cmd)
        
        ssid = 'N/A'
        bssid = 'N/A'
        rssi = -100
        
        for line in result.split('\n'):
            line = line.strip()
            
            # SSID
            if 'SSID:' in line:
                ssid = line.split('SSID:')[1].strip()
            
            # BSSID
            elif 'Connected to' in line:
                bssid = line.split('Connected to')[1].strip()
            
            # RSSI
            elif 'signal:' in line:
                match = re.search(r'signal:\s*([-\d]+)', line)
                if match:
                    rssi = int(match.group(1).strip())
        
        # Se não encontrou, tentar scan
        if ssid == 'N/A' or bssid == 'N/A':
            scan_result = sta.cmd(f'iw dev {sta_name}-wlan0 scan')
            for line in scan_result.split('\n'):
                if 'SSID:' in line and ssid == 'N/A':
                    ssid = line.split('SSID:')[1].strip()
                elif 'BSS' in line and bssid == 'N/A':
                    bssid = line.split()[1]
        
        return {
            'SSID': ssid,
            'BSSID': bssid,
            'Signal Level (dBm)': rssi
        }
        
    except Exception as e:
        return {
            'SSID': 'N/A',
            'BSSID': 'N/A', 
            'Signal Level (dBm)': -100
        }

def obter_latencia_completa(sta):
    """Obtém latência com packet loss"""
    try:
        ping_result = sta.cmd('ping -c 1 -W 2 10.0.0.1')
        
        if '1 received' in ping_result or '1 packets received' in ping_result:
            # Extrair latência
            for line in ping_result.split('\n'):
                if 'time=' in line:
                    match = re.search(r'time=([\d.]+)', line)
                    if match:
                        latency = float(match.group(1))
                        return {
                            'latency_ms': latency,
                            'packet_loss': False
                        }
        
        return {
            'latency_ms': 9999.0,
            'packet_loss': True
        }
        
    except Exception as e:
        return {
            'latency_ms': 9999.0,
            'packet_loss': True
        }

def obter_bandwidth_iperf3(sta):
    """Obtém bandwidth usando iperf3"""
    try:
        # Iniciar servidor iperf3 em background
        server_cmd = "iperf3 -s -D"
        sta.cmd(server_cmd)
        time.sleep(1)
        
        # Executar teste de download
        client_cmd = "iperf3 -c 127.0.0.1 -t 2 -J"
        result = sta.cmd(client_cmd)
        
        # Parar servidor
        sta.cmd("pkill iperf3")
        
        # Parsear resultado JSON
        try:
            data = json.loads(result)
            if 'end' in data and 'streams' in data['end']:
                bandwidth = data['end']['streams'][0]['receiver']['bits_per_second'] / 1000000  # Mbps
                return {'bandwidth_mbps': bandwidth}
        except:
            pass
        
        return {'error': 'iperf3 falhou'}
        
    except Exception as e:
        return {'error': 'iperf3 falhou'}

def detectar_handover(sta, sta_name, ap_objs, ap_anterior):
    """Detecta handover entre APs"""
    try:
        # Obter AP atual
        cmd = f"iw dev {sta_name}-wlan0 link"
        result = sta.cmd(cmd)
        
        if 'Not connected' in result or 'No such device' in result:
            return {'handover': False}
        
        # Tentar identificar AP por ping
        for ap_name, ap in ap_objs.items():
            try:
                ap_ip = f"10.0.0.{list(ap_objs.keys()).index(ap_name) + 1}"
                ping_result = sta.cmd(f'ping -c 1 -W 1 {ap_ip}')
                
                if '1 received' in ping_result or '1 packets received' in ping_result:
                    ap_atual = ap_name
                    break
            except:
                continue
        else:
            ap_atual = 'conectado_desconhecido'
        
        # Se mudou de AP
        if ap_anterior and ap_atual != ap_anterior and ap_atual != 'conectado_desconhecido':
            return {
                'handover': True,
                'new_bssid': ap_atual
            }
        
        return {'handover': False}
        
    except Exception as e:
        return {'handover': False}

def executar_simulacao_mesh_v4(config):
    """Executa simulação mesh com coleta completa de dados"""
    
    info("*** 🚀 Iniciando DSL Mininet-WiFi v4.0 SUPER COMPLETA\n")
    
    # Criar rede
    net = Mininet_wifi(controller=Controller)
    
    # Adicionar controller
    info("*** Adicionando controller\n")
    c0 = net.addController('c0', controller=Controller, ip='127.0.0.1', port=6633)
    
    # Adicionar APs
    info("*** Adicionando APs\n")
    ap_objs = {}
    for ap_conf in config["aps"]:
        ap = net.addAccessPoint(
            ap_conf["name"], 
            ssid=ap_conf["ssid"],
            mode="g", 
            channel=ap_conf.get("channel", 1),
            position=f'{ap_conf["x"]},{ap_conf["y"]},0',
            range=ap_conf.get("range", 30)
        )
        ap_objs[ap_conf["name"]] = ap
        info(f"   📡 AP {ap_conf['name']} em ({ap_conf['x']}, {ap_conf['y']})\n")
    
    # Adicionar stations
    info("*** Adicionando stations\n")
    sta_objs = {}
    for sta_conf in config["stations"]:
        sta = net.addStation(
            sta_conf["name"],
            position=f'{sta_conf["start_x"]},{sta_conf["start_y"]},0'
        )
        sta_objs[sta_conf["name"]] = sta
        info(f"   📱 Station {sta_conf['name']} em ({sta_conf['start_x']}, {sta_conf['start_y']})\n")
    
    # Configurar rede
    info("*** Configurando rede\n")
    net.configureWifiNodes()
    
    # Iniciar rede
    info("*** Iniciando rede\n")
    net.build()
    c0.start()
    
    for ap in ap_objs.values():
        ap.start([c0])
    
    # Aguardar estabilização
    info("*** Aguardando estabilização da rede\n")
    time.sleep(5)
    
    # Criar diretório de resultados
    os.makedirs('results', exist_ok=True)
    
    # Executar simulação para cada station
    for sta_conf in config["stations"]:
        sta = sta_objs[sta_conf["name"]]
        
        info(f"*** 🚗 Iniciando simulação para {sta_conf['name']}\n")
        
        # Criar arquivo de log
        log_file = f'results/{sta_conf["name"]}_v4_log.csv'
        
        with open(log_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'wifi_info', 'latency_info', 'bandwidth_info', 'handover_info']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Dados iniciais
            ap_anterior = None
            
            # Posição inicial
            wifi_info = obter_info_wifi_detalhada(sta, sta_conf["name"])
            latency_info = obter_latencia_completa(sta)
            bandwidth_info = obter_bandwidth_iperf3(sta)
            handover_info = detectar_handover(sta, sta_conf["name"], ap_objs, ap_anterior)
            
            # Determinar AP atual
            ap_atual = None
            for ap_name, ap in ap_objs.items():
                try:
                    ap_ip = f"10.0.0.{list(ap_objs.keys()).index(ap_name) + 1}"
                    ping_result = sta.cmd(f'ping -c 1 -W 1 {ap_ip}')
                    if '1 received' in ping_result or '1 packets received' in ping_result:
                        ap_atual = ap_name
                        break
                except:
                    continue
            
            ap_anterior = ap_atual
            
            writer.writerow({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'wifi_info': str([wifi_info]),
                'latency_info': str(latency_info),
                'bandwidth_info': str(bandwidth_info),
                'handover_info': str(handover_info)
            })
            
            info(f"   📊 Dados iniciais: {wifi_info} | {latency_info} | {bandwidth_info} | {handover_info}\n")
            
            # Mover pela trajetória
            for i, point in enumerate(sta_conf["trajectory"]):
                x, y = point
                
                info(f"   🚗 Movendo para ({x}, {y})\n")
                sta.setPosition(f'{x},{y},0')
                time.sleep(config.get("wait", 3))
                
                # Coletar dados completos
                wifi_info = obter_info_wifi_detalhada(sta, sta_conf["name"])
                latency_info = obter_latencia_completa(sta)
                bandwidth_info = obter_bandwidth_iperf3(sta)
                handover_info = detectar_handover(sta, sta_conf["name"], ap_objs, ap_anterior)
                
                # Determinar AP atual
                ap_atual = None
                for ap_name, ap in ap_objs.items():
                    try:
                        ap_ip = f"10.0.0.{list(ap_objs.keys()).index(ap_name) + 1}"
                        ping_result = sta.cmd(f'ping -c 1 -W 1 {ap_ip}')
                        if '1 received' in ping_result or '1 packets received' in ping_result:
                            ap_atual = ap_name
                            break
                    except:
                        continue
                
                # Atualizar handover se necessário
                if ap_anterior and ap_atual and ap_atual != ap_anterior:
                    handover_info = {
                        'handover': True,
                        'new_bssid': ap_atual
                    }
                
                ap_anterior = ap_atual
                
                writer.writerow({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'wifi_info': str([wifi_info]),
                    'latency_info': str(latency_info),
                    'bandwidth_info': str(bandwidth_info),
                    'handover_info': str(handover_info)
                })
                
                info(f"   📊 Dados: {wifi_info} | {latency_info} | {bandwidth_info} | {handover_info}\n")
    
    info("*** ✅ Simulação v4.0 concluída!\n")
    info("*** 📁 Logs salvos em results/\n")
    
    # Encerrar rede
    info("*** 🛑 Encerrando rede\n")
    net.stop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: sudo python3 executa_cenario_mesh_v4.py <arquivo_config.json>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        executar_simulacao_mesh_v4(config)
        
    except FileNotFoundError:
        error(f"❌ Arquivo de configuração não encontrado: {config_file}\n")
        sys.exit(1)
    except json.JSONDecodeError as e:
        error(f"❌ Erro no JSON do arquivo de configuração: {e}\n")
        sys.exit(1)
    except Exception as e:
        error(f"❌ Erro durante execução: {e}\n")
        sys.exit(1)
