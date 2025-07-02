#!/usr/bin/env python3
"""
Script para simular Raspberry Pi móvel coletando dados em tempo real
Simula um dispositivo embarcado em um carrinho coletando dados de rede
"""

import json
import time
import csv
import os
import re
import sys
from datetime import datetime
from mininet.log import info
from mininet_wifi.net import Mininet_wifi
from mininet_wifi.node import Controller, OVSKernelAP

def obter_rssi_raspberry(sta, sta_name):
    """Simula coleta de RSSI pelo Raspberry Pi"""
    try:
        # Comando que o Raspberry Pi executaria
        cmd = f"iw dev {sta_name}-wlan0 link"
        result = sta.cmd(cmd)
        
        for line in result.split('\n'):
            if 'signal:' in line:
                match = re.search(r'signal:\s*([-\d]+)', line)
                if match:
                    return int(match.group(1).strip())
        
        # Fallback se não conseguir obter RSSI
        return -100
    except Exception as e:
        info(f"Erro ao obter RSSI: {e}\n")
        return -100

def obter_latencia_raspberry(sta):
    """Simula teste de latência pelo Raspberry Pi"""
    try:
        # Ping para gateway (como o Raspberry faria)
        ping_result = sta.cmd('ping -c 1 -W 2 10.0.0.1')
        
        for line in ping_result.split('\n'):
            if 'time=' in line:
                match = re.search(r'time=([\d.]+)', line)
                if match:
                    return float(match.group(1))
        
        return 9999.0  # Timeout
    except Exception as e:
        info(f"Erro ao obter latência: {e}\n")
        return 9999.0

def obter_ap_conectado_raspberry(sta, sta_name, ap_objs):
    """Simula detecção de AP conectado pelo Raspberry Pi"""
    try:
        # Verificar se está conectado
        cmd = f"iw dev {sta_name}-wlan0 link"
        result = sta.cmd(cmd)
        
        if 'Not connected' in result:
            return 'desconectado'
        
        # Tentar determinar qual AP está respondendo melhor
        # Simula o que o Raspberry Pi faria: testar conectividade com cada AP
        melhor_ap = None
        melhor_rssi = -100
        
        for ap_name, ap in ap_objs.items():
            try:
                # Tentar ping para cada AP
                ap_ip = f"10.0.0.{list(ap_objs.keys()).index(ap_name) + 1}"
                ping_result = sta.cmd(f'ping -c 1 -W 1 {ap_ip}')
                
                if '1 received' in ping_result:
                    # Se respondeu, verificar RSSI para este AP
                    rssi = obter_rssi_raspberry(sta, sta_name)
                    if rssi > melhor_rssi:
                        melhor_rssi = rssi
                        melhor_ap = ap_name
            except:
                continue
        
        return melhor_ap if melhor_ap else 'conectado_desconhecido'
        
    except Exception as e:
        return 'erro_conexao'

def obter_qualidade_sinal(rssi):
    """Converte RSSI em qualidade de sinal (como o Raspberry Pi faria)"""
    if rssi >= -50:
        return "Excelente"
    elif rssi >= -60:
        return "Muito Boa"
    elif rssi >= -70:
        return "Boa"
    elif rssi >= -80:
        return "Regular"
    else:
        return "Ruim"

def obter_qualidade_latencia(latencia):
    """Converte latência em qualidade (como o Raspberry Pi faria)"""
    if latencia < 50:
        return "Excelente"
    elif latencia < 100:
        return "Muito Boa"
    elif latencia < 200:
        return "Boa"
    elif latencia < 500:
        return "Regular"
    else:
        return "Ruim"

def scan_wifi(sta, sta_name):
    """Faz scan Wi-Fi e retorna string com APs visíveis e seus sinais"""
    try:
        scan_result = sta.cmd(f'iw dev {sta_name}-wlan0 scan')
        aps = []
        current_bssid = None
        current_signal = None
        for line in scan_result.split('\n'):
            line = line.strip()
            if line.startswith('BSS '):
                current_bssid = line.split()[1]
                current_signal = None
            elif 'signal:' in line:
                try:
                    current_signal = int(float(line.split('signal:')[1].split()[0]))
                except:
                    current_signal = None
            elif 'SSID:' in line and current_bssid and current_signal is not None:
                ssid = line.split('SSID:')[1].strip()
                aps.append(f"{ssid}:{current_signal}")
                current_bssid = None
                current_signal = None
        return ';'.join(aps)
    except Exception as e:
        return ''

def simular_raspberry_pi_movel(config):
    """Simula Raspberry Pi móvel coletando dados"""
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

    info("*** 🏢 Criando APs (Pontos de Acesso Fixos)\n")
    ap_objs = {}
    for ap in config["aps"]:
        ap_objs[ap["name"]] = net.addAccessPoint(
            ap["name"],
            ssid=config.get("ssid", "meshNet"),
            mode="g",
            channel=str(config.get("channel", 1)),
            position=f'{ap["x"]},{ap["y"]},0'
        )
        info(f"   📡 {ap['name']} em ({ap['x']}, {ap['y']})\n")

    info("*** 🤖 Criando Raspberry Pi Móvel\n")
    sta_objs = {}
    for sta in config["stations"]:
        sta_objs[sta["name"]] = net.addStation(
            sta["name"],
            position=f'{sta["start_x"]},{sta["start_y"]},0'
        )
        info(f"   📱 {sta['name']} iniciando em ({sta['start_x']}, {sta['start_y']})\n")

    c1 = net.addController('c1')
    net.configureWifiNodes()

    info("*** 🌐 Iniciando Rede WiFi\n")
    net.build()
    c1.start()
    for ap in ap_objs.values():
        ap.start([c1])

    # Aguardar estabilização da rede
    info("*** ⏳ Aguardando estabilização da rede (3s)\n")
    time.sleep(3)

    info("*** 🚗 Iniciando Movimento do Raspberry Pi\n")
    for sta_conf in config["stations"]:
        sta = sta_objs[sta_conf["name"]]
        
        # Criar arquivo de log do Raspberry Pi
        os.makedirs('results', exist_ok=True)
        log_file = f'raspberry_pi_{sta_conf["name"]}_log.csv'
        log_path = os.path.join('results', log_file)
        
        with open(log_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'timestamp', 'x', 'y', 'rssi_dbm', 'qualidade_sinal', 
                'latencia_ms', 'qualidade_latencia', 'ap_conectado', 
                'status_conexao', 'handover_detectado', 'aps_visiveis'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Coleta inicial (posição de partida)
            info(f"📍 Posição inicial: ({sta_conf['start_x']}, {sta_conf['start_y']})\n")
            
            rssi = obter_rssi_raspberry(sta, sta_conf["name"])
            latencia = obter_latencia_raspberry(sta)
            ap_conectado = obter_ap_conectado_raspberry(sta, sta_conf["name"], ap_objs)
            
            # Determinar status da conexão
            status_conexao = "Conectado" if ap_conectado != 'desconectado' else "Desconectado"
            
            aps_visiveis = scan_wifi(sta, sta_conf["name"])
            writer.writerow({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'x': sta_conf["start_x"],
                'y': sta_conf["start_y"],
                'rssi_dbm': rssi,
                'qualidade_sinal': obter_qualidade_sinal(rssi),
                'latencia_ms': latencia,
                'qualidade_latencia': obter_qualidade_latencia(latencia),
                'ap_conectado': ap_conectado,
                'status_conexao': status_conexao,
                'handover_detectado': 'Não',
                'aps_visiveis': aps_visiveis
            })
            
            info(f"   📊 Dados coletados: RSSI={rssi}dBm, Latência={latencia}ms, AP={ap_conectado}\n")

            # Mover pela trajetória e coletar dados
            ap_anterior = ap_conectado
            for i, point in enumerate(sta_conf["trajectory"]):
                x, y = point
                
                info(f"🚗 Movendo para: ({x}, {y})\n")
                sta.setPosition(f'{x},{y},0')
                time.sleep(config.get("wait", 3))  # Aguardar estabilização

                # Coletar dados na nova posição
                rssi = obter_rssi_raspberry(sta, sta_conf["name"])
                latencia = obter_latencia_raspberry(sta)
                ap_conectado = obter_ap_conectado_raspberry(sta, sta_conf["name"], ap_objs)
                
                # Detectar handover
                handover_detectado = 'Sim' if ap_anterior != ap_conectado and ap_conectado != 'desconectado' else 'Não'
                
                # Determinar status da conexão
                status_conexao = "Conectado" if ap_conectado != 'desconectado' else "Desconectado"
                
                aps_visiveis = scan_wifi(sta, sta_conf["name"])
                writer.writerow({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'x': x,
                    'y': y,
                    'rssi_dbm': rssi,
                    'qualidade_sinal': obter_qualidade_sinal(rssi),
                    'latencia_ms': latencia,
                    'qualidade_latencia': obter_qualidade_latencia(latencia),
                    'ap_conectado': ap_conectado,
                    'status_conexao': status_conexao,
                    'handover_detectado': handover_detectado,
                    'aps_visiveis': aps_visiveis
                })
                
                info(f"   📊 Dados coletados: RSSI={rssi}dBm, Latência={latencia}ms, AP={ap_conectado}")
                if handover_detectado == 'Sim':
                    info(f" 🔄 HANDOVER DETECTADO: {ap_anterior} → {ap_conectado}")
                info("\n")
                
                ap_anterior = ap_conectado

    info("*** ✅ Coleta de dados concluída\n")
    info(f"*** 📁 Log salvo em: {log_path}\n")
    
    info("*** 🛑 Encerrando rede\n")
    net.stop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("🤖 Uso: python3 executa_raspberry_movel.py <arquivo_cenario.json>")
        print("📋 Exemplo: python3 executa_raspberry_movel.py cenarios/cenario_raspberry_movel.json")
        sys.exit(1)
    
    arquivo_cenario = sys.argv[1]
    
    try:
        with open(arquivo_cenario, 'r') as f:
            config = json.load(f)
        
        print("🤖 Iniciando Simulação do Raspberry Pi Móvel")
        print("=" * 50)
        simular_raspberry_pi_movel(config)
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo {arquivo_cenario} não encontrado")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Erro: Arquivo {arquivo_cenario} não é um JSON válido")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1) 