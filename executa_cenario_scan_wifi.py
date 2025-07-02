#!/usr/bin/env python3
"""
Script para simular Raspberry Pi móvel com scan Wi-Fi
Coleta dados de RSSI, latência, AP conectado e scan de todas as redes visíveis
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

def obter_rssi(sta, sta_name):
    """Obtém o RSSI da station"""
    try:
        cmd = f"iw dev {sta_name}-wlan0 link"
        result = sta.cmd(cmd)
        
        for line in result.split('\n'):
            if 'signal:' in line:
                match = re.search(r'signal:\s*([-\d]+)', line)
                if match:
                    return int(match.group(1).strip())
        return -100
    except Exception as e:
        return -100

def obter_latencia(sta):
    """Obtém a latência"""
    try:
        ping_result = sta.cmd('ping -c 1 -W 2 10.0.0.1')
        for line in ping_result.split('\n'):
            if 'time=' in line:
                match = re.search(r'time=([\d.]+)', line)
                if match:
                    return float(match.group(1))
        return 9999.0
    except Exception as e:
        return 9999.0

def obter_ap_especifico(sta, sta_name, ap_objs):
    """Obtém qual AP específico a station está conectada"""
    try:
        cmd = f"iw dev {sta_name}-wlan0 link"
        result = sta.cmd(cmd)
        
        if 'Not connected' in result or 'No such device' in result:
            return 'desconectado'
        
        for ap_name, ap in ap_objs.items():
            try:
                ap_ip = f"10.0.0.{list(ap_objs.keys()).index(ap_name) + 1}"
                ping_result = sta.cmd(f'ping -c 1 -W 1 {ap_ip}')
                
                if '1 received' in ping_result or '1 packets received' in ping_result:
                    return ap_name
            except:
                continue
        
        return 'conectado_desconhecido'
    except Exception as e:
        return 'erro_conexao'

def scan_wifi_completo(sta, sta_name):
    """Faz scan Wi-Fi completo e retorna string com APs visíveis e seus sinais"""
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
                aps_visiveis.append(f"{current_ssid}:{current_signal}")
                current_bssid = None
                current_signal = None
                current_ssid = None
        
        return ';'.join(aps_visiveis) if aps_visiveis else 'nenhum_ap_detectado'
        
    except Exception as e:
        info(f"Erro no scan Wi-Fi: {e}\n")
        return 'erro_scan'

def obter_qualidade_sinal(rssi):
    """Converte RSSI em qualidade de sinal"""
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
    """Converte latência em qualidade"""
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

def executar_simulacao_scan_wifi(config):
    """Executa simulação com scan Wi-Fi completo"""
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

    info("*** 🚗 Iniciando Movimento do Raspberry Pi com Scan Wi-Fi\n")
    for sta_conf in config["stations"]:
        sta = sta_objs[sta_conf["name"]]
        
        # Criar arquivo de log do Raspberry Pi
        os.makedirs('results', exist_ok=True)
        log_file = f'raspberry_pi_scan_{sta_conf["name"]}_log.csv'
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
            
            rssi = obter_rssi(sta, sta_conf["name"])
            latencia = obter_latencia(sta)
            ap_conectado = obter_ap_especifico(sta, sta_conf["name"], ap_objs)
            aps_visiveis = scan_wifi_completo(sta, sta_conf["name"])
            
            # Determinar status da conexão
            status_conexao = "Conectado" if ap_conectado != 'desconectado' else "Desconectado"
            
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
            
            info(f"   📊 Dados coletados: RSSI={rssi}dBm, Latência={latencia}ms, AP={ap_conectado}")
            info(f"   📡 APs visíveis: {aps_visiveis}\n")

            # Mover pela trajetória e coletar dados
            ap_anterior = ap_conectado
            for i, point in enumerate(sta_conf["trajectory"]):
                x, y = point
                
                info(f"🚗 Movendo para: ({x}, {y})\n")
                sta.setPosition(f'{x},{y},0')
                time.sleep(config.get("wait", 3))  # Aguardar estabilização

                # Coletar dados na nova posição
                rssi = obter_rssi(sta, sta_conf["name"])
                latencia = obter_latencia(sta)
                ap_conectado = obter_ap_especifico(sta, sta_conf["name"], ap_objs)
                aps_visiveis = scan_wifi_completo(sta, sta_conf["name"])
                
                # Detectar handover
                handover_detectado = 'Sim' if ap_anterior != ap_conectado and ap_conectado != 'desconectado' else 'Não'
                
                # Determinar status da conexão
                status_conexao = "Conectado" if ap_conectado != 'desconectado' else "Desconectado"
                
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
                info(f"   📡 APs visíveis: {aps_visiveis}")
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
        print("🤖 Uso: python3 executa_cenario_scan_wifi.py <arquivo_cenario.json>")
        print("📋 Exemplo: python3 executa_cenario_scan_wifi.py cenarios/cenario_raspberry_movel.json")
        sys.exit(1)
    
    arquivo_cenario = sys.argv[1]
    
    try:
        with open(arquivo_cenario, 'r') as f:
            config = json.load(f)
        
        print("🤖 Iniciando Simulação do Raspberry Pi Móvel com Scan Wi-Fi")
        print("=" * 60)
        executar_simulacao_scan_wifi(config)
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo {arquivo_cenario} não encontrado")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Erro: Arquivo {arquivo_cenario} não é um JSON válido")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1) 