#!/usr/bin/python

import json
import time
import csv
import sys
from mininet.wifi.net import Mininet_wifi
from mininet.wifi.node import OVSKernelAP
from mininet.node import Controller
from mininet.log import setLogLevel, info

def carregar_config(arquivo):
    with open(arquivo, 'r') as f:
        return json.load(f)

def executar_simulacao(config):
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

    info("*** Criando APs\n")
    ap_objs = {}
    for ap in config["aps"]:
        ap_objs[ap["name"]] = net.addAccessPoint(
            ap["name"],
            ssid="meshNet",
            mode="g",
            channel="1",
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

    info("*** Movimentando stations\n")
    for sta_conf in config["stations"]:
        sta = sta_objs[sta_conf["name"]]
        log_file = f'{sta_conf["name"]}_log.csv'
        with open(log_file, 'w', newline='') as csvfile:
            fieldnames = ['time', 'position', 'rssi', 'latency_ms']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for point in sta_conf["trajectory"]:
                x, y = point
                sta.setPosition(f'{x},{y},0')
                time.sleep(config["wait"])

                rssi = sta.cmd("iw dev %s-wlan0 link | grep signal | awk '{print $2}'" % sta_conf["name"])
                if rssi == '':
                    rssi = '-100'

                ping_result = sta.cmd('ping -c 1 -W 1 8.8.8.8')
                if "time=" in ping_result:
                    latency_line = [line for line in ping_result.split('\n') if "time=" in line][0]
                    latency_ms = latency_line.split('time=')[1].split(' ')[0]
                else:
                    latency_ms = '9999'

                writer.writerow({
                    'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'position': f'{x},{y}',
                    'rssi': rssi,
                    'latency_ms': latency_ms
                })
                info(f"{sta_conf['name']} → pos=({x},{y}) RSSI={rssi} latency={latency_ms}\n")

    info("*** Encerrando rede\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    if len(sys.argv) < 2:
        print("Uso: python3 executa_cenario.py cenario.json")
        sys.exit(1)
    conf = carregar_config(sys.argv[1])
    executar_simulacao(conf) 