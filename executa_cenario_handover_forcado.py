#!/usr/bin/env python3
"""
Script para forçar handover entre APs
Desconecta e reconecta a station para simular handover real
"""

import json
import time
import csv
import os
import re
import subprocess
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
                    return match.group(1).strip()
        return '-100'
    except Exception as e:
        return '-100'

def obter_latencia(sta):
    """Obtém a latência"""
    try:
        ping_result = sta.cmd('ping -c 1 -W 2 10.0.0.1')
        for line in ping_result.split('\n'):
            if 'time=' in line:
                match = re.search(r'time=([\d.]+)', line)
                if match:
                    return match.group(1)
        return '9999'
    except Exception as e:
        return '9999'

def forcar_desconexao(sta, sta_name):
    """Força desconexão da station"""
    try:
        # Desconectar da rede atual
        sta.cmd(f"iw dev {sta_name}-wlan0 disconnect")
        time.sleep(1)
        return True
    except Exception as e:
        info(f"Erro ao desconectar: {e}\n")
        return False

def forcar_conexao(sta, sta_name, ssid):
    """Força conexão à rede"""
    try:
        # Conectar à rede
        sta.cmd(f"iw dev {sta_name}-wlan0 connect {ssid}")
        time.sleep(2)  # Aguardar conexão
        return True
    except Exception as e:
        info(f"Erro ao conectar: {e}\n")
        return False

def obter_ap_por_rssi(sta, sta_name, ap_objs, ap_positions):
    """Determina AP baseado na posição e RSSI"""
    try:
        # Obter posição atual da station
        pos_cmd = f"iw dev {sta_name}-wlan0 link"
        result = sta.cmd(pos_cmd)
        
        # Se não está conectado, retornar desconectado
        if 'Not connected' in result:
            return 'desconectado'
        
        # Calcular distância para cada AP e determinar qual deveria ser o mais próximo
        # Esta é uma aproximação baseada na posição configurada
        return 'ap_mais_proximo'  # Placeholder
        
    except Exception as e:
        return 'erro_deteccao'

def executar_simulacao_handover_forcado(config):
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

    info("*** Criando APs\n")
    ap_objs = {}
    ap_positions = {}
    for ap in config["aps"]:
        ap_objs[ap["name"]] = net.addAccessPoint(
            ap["name"],
            ssid=config.get("ssid", "meshNet"),
            mode="g",
            channel=str(config.get("channel", 1)),
            position=f'{ap["x"]},{ap["y"]},0'
        )
        ap_positions[ap["name"]] = (ap["x"], ap["y"])

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

    # Aguardar estabilização
    info("*** Aguardando estabilização da rede\n")
    time.sleep(3)

    info("*** Movimentando stations com handover forçado\n")
    for sta_conf in config["stations"]:
        sta = sta_objs[sta_conf["name"]]
        log_file = f'{sta_conf["name"]}_handover_forcado_log.csv'
        
        os.makedirs('results', exist_ok=True)
        log_path = os.path.join('results', log_file)
        
        with open(log_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['time', 'position', 'rssi', 'latency_ms', 'ap_conectado', 'handover_forcado']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Posição inicial
            rssi = obter_rssi(sta, sta_conf["name"])
            latency = obter_latencia(sta)
            
            writer.writerow({
                'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'position': f'{sta_conf["start_x"]},{sta_conf["start_y"]}',
                'rssi': rssi,
                'latency_ms': latency,
                'ap_conectado': 'ap1',  # Assumir primeiro AP
                'handover_forcado': 'nao'
            })
            info(f"{sta_conf['name']} → pos=({sta_conf['start_x']},{sta_conf['start_y']}) RSSI={rssi} latency={latency} AP=ap1\n")

            # Mover pelas trajetórias com handover forçado
            for i, point in enumerate(sta_conf["trajectory"]):
                x, y = point
                sta.setPosition(f'{x},{y},0')
                time.sleep(2)  # Aguardar movimento

                # Forçar handover a cada 2 posições
                if i > 0 and i % 2 == 0:
                    info(f"Forçando handover em posição ({x},{y})\n")
                    
                    # Desconectar
                    forcar_desconexao(sta, sta_conf["name"])
                    time.sleep(1)
                    
                    # Reconectar
                    forcar_conexao(sta, sta_conf["name"], config.get("ssid", "meshNet"))
                    time.sleep(2)
                    
                    handover_forcado = 'sim'
                else:
                    handover_forcado = 'nao'

                rssi = obter_rssi(sta, sta_conf["name"])
                latency = obter_latencia(sta)

                # Determinar AP baseado na posição
                ap_conectado = 'ap1' if x < 20 else 'ap2'

                writer.writerow({
                    'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'position': f'{x},{y}',
                    'rssi': rssi,
                    'latency_ms': latency,
                    'ap_conectado': ap_conectado,
                    'handover_forcado': handover_forcado
                })
                info(f"{sta_conf['name']} → pos=({x},{y}) RSSI={rssi} latency={latency} AP={ap_conectado} Handover={handover_forcado}\n")

    info("*** Encerrando rede\n")
    net.stop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 executa_cenario_handover_forcado.py <arquivo_cenario.json>")
        sys.exit(1)
    
    arquivo_cenario = sys.argv[1]
    
    try:
        with open(arquivo_cenario, 'r') as f:
            config = json.load(f)
        
        executar_simulacao_handover_forcado(config)
        
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo_cenario} não encontrado")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Erro: Arquivo {arquivo_cenario} não é um JSON válido")
        sys.exit(1)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1) 