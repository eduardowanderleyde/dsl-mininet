#!/usr/bin/python3

import json
import time
import csv
import sys
import os
import re
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mininet.node import Controller
from mininet.log import setLogLevel, info

def carregar_config(arquivo):
    with open(arquivo, 'r') as f:
        return json.load(f)

def obter_rssi(sta, sta_name):
    """Obtém o RSSI da station de forma mais robusta"""
    try:
        # Tentar obter RSSI usando iw dev
        cmd = f"iw dev {sta_name}-wlan0 link"
        result = sta.cmd(cmd)
        
        # Procurar por "signal:" no resultado
        for line in result.split('\n'):
            if 'signal:' in line:
                # Extrair valor numérico
                match = re.search(r'signal:\s*([-\d]+)', line)
                if match:
                    return match.group(1).strip()
        
        # Fallback: tentar com iwconfig
        cmd = f"iwconfig {sta_name}-wlan0 | grep -i quality"
        result = sta.cmd(cmd)
        for line in result.split('\n'):
            if 'signal level' in line.lower():
                match = re.search(r'signal level[=:]\s*([-\d]+)', line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        return '-100'  # Valor padrão se não conseguir obter
    except Exception as e:
        info(f"Erro ao obter RSSI: {e}\n")
        return '-100'

def obter_latencia(sta):
    """Obtém a latência de forma mais robusta"""
    try:
        # Tentar ping para o AP primeiro
        ping_result = sta.cmd('ping -c 1 -W 2 10.0.0.1')
        
        # Procurar por "time=" no resultado
        for line in ping_result.split('\n'):
            if 'time=' in line:
                match = re.search(r'time=([\d.]+)', line)
                if match:
                    return match.group(1)
        
        # Fallback: tentar ping para 8.8.8.8
        ping_result = sta.cmd('ping -c 1 -W 2 8.8.8.8')
        for line in ping_result.split('\n'):
            if 'time=' in line:
                match = re.search(r'time=([\d.]+)', line)
                if match:
                    return match.group(1)
        
        return '9999'  # Timeout se não conseguir
    except Exception as e:
        info(f"Erro ao obter latência: {e}\n")
        return '9999'

def executar_simulacao(config):
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

    info("*** Criando APs\n")
    ap_objs = {}
    for ap in config["aps"]:
        ap_objs[ap["name"]] = net.addAccessPoint(
            ap["name"],
            ssid=config.get("ssid", "meshNet"),
            mode="g",
            channel=str(config.get("channel", 1)),
            position=f'{ap["x"]},{ap["y"]},0'
        )

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

    info("*** Movimentando stations\n")
    for sta_conf in config["stations"]:
        sta = sta_objs[sta_conf["name"]]
        log_file = f'{sta_conf["name"]}_log.csv'
        
        # Criar diretório results se não existir
        os.makedirs('results', exist_ok=True)
        log_path = os.path.join('results', log_file)
        
        with open(log_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['time', 'position', 'rssi', 'latency_ms']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Log da posição inicial
            rssi = obter_rssi(sta, sta_conf["name"])
            latency = obter_latencia(sta)
            
            writer.writerow({
                'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'position': f'{sta_conf["start_x"]},{sta_conf["start_y"]}',
                'rssi': rssi,
                'latency_ms': latency
            })
            info(f"{sta_conf['name']} → pos=({sta_conf['start_x']},{sta_conf['start_y']}) RSSI={rssi} latency={latency}\n")

            # Mover pelas trajetórias
            for point in sta_conf["trajectory"]:
                x, y = point
                sta.setPosition(f'{x},{y},0')
                time.sleep(config.get("wait", 2))

                rssi = obter_rssi(sta, sta_conf["name"])
                latency = obter_latencia(sta)

                writer.writerow({
                    'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'position': f'{x},{y}',
                    'rssi': rssi,
                    'latency_ms': latency
                })
                info(f"{sta_conf['name']} → pos=({x},{y}) RSSI={rssi} latency={latency}\n")

    info("*** Encerrando rede\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    if len(sys.argv) < 2:
        print("Uso: python3 executa_cenario.py cenario.json")
        sys.exit(1)
    conf = carregar_config(sys.argv[1])
    executar_simulacao(conf) 