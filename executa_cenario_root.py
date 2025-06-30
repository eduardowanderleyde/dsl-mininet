#!/usr/bin/env python3

import json
import sys
import os
import time
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
from mn_wifi.mobility import mobility
from mn_wifi.plot import plotGraph
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mininet.cli import CLI

def carregar_configuracao(arquivo):
    """Carrega a configuração do cenário a partir do arquivo JSON"""
    with open(arquivo, 'r') as f:
        return json.load(f)

def criar_rede(config):
    """Cria a rede Mininet-WiFi baseada na configuração"""
    info("*** Criando rede Mininet-WiFi\n")
    
    # Criar rede
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                      wmediumd_mode=interference, noise_threshold=-91,
                      fading_coefficient=0)
    
    # Criar APs
    aps = []
    for ap_config in config['aps']:
        ap = net.addAccessPoint(ap_config['name'], ssid=config['ssid'],
                               channel=config['channel'], mode='g',
                               position=f"{ap_config['x']},{ap_config['y']},0")
        aps.append(ap)
    
    # Criar stations
    stations = []
    for sta_config in config['stations']:
        sta = net.addStation(sta_config['name'],
                           position=f"{sta_config['start_x']},{sta_config['start_y']},0")
        stations.append(sta)
    
    # Configurar trajetórias
    if config['stations']:
        net.setMobilityModel(time=0, model='RandomDirection',
                           max_x=100, max_y=100, seed=20)
    
    # Configurar trajetórias específicas se fornecidas
    for i, sta_config in enumerate(config['stations']):
        if sta_config['trajectory']:
            # Converter trajetória para formato do Mininet-WiFi
            traj_points = []
            for point in sta_config['trajectory']:
                traj_points.append(f"{point[0]},{point[1]},0")
            
            # Configurar trajetória personalizada
            net.mobility(stations[i], 'start', time=0,
                        position=f"{sta_config['start_x']},{sta_config['start_y']},0")
            
            for j, point in enumerate(traj_points):
                net.mobility(stations[i], 'stop', time=j+1, position=point)
    
    # Configurar controller
    c0 = net.addController('c0', controller=Controller)
    
    return net, aps, stations

def executar_simulacao(net, config):
    """Executa a simulação"""
    info("*** Configurando rede\n")
    net.configureWifiNodes()
    
    info("*** Iniciando rede\n")
    net.build()
    c0 = net.get('c0')
    c0.start()
    
    for ap in net.aps:
        ap.start([c0])
    
    info("*** Aguardando estabilização da rede\n")
    time.sleep(config.get('wait', 2))
    
    info("*** Executando CLI\n")
    CLI(net)
    
    info("*** Parando rede\n")
    net.stop()

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 executa_cenario_root.py <arquivo_config.json>")
        sys.exit(1)
    
    arquivo_config = sys.argv[1]
    
    if not os.path.exists(arquivo_config):
        print(f"Erro: Arquivo {arquivo_config} não encontrado")
        sys.exit(1)
    
    try:
        # Configurar logging
        setLogLevel('info')
        
        # Carregar configuração
        config = carregar_configuracao(arquivo_config)
        print(f"Cenário carregado: {config['ssid']}")
        print(f"APs: {len(config['aps'])}")
        print(f"Stations: {len(config['stations'])}")
        
        # Criar e executar rede
        net, aps, stations = criar_rede(config)
        executar_simulacao(net, config)
        
    except Exception as e:
        print(f"Erro durante execução: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 