#!/usr/bin/python3

import json
import time
import csv
import sys
import os
import re
import subprocess
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
        cmd = f"iw dev {sta_name}-wlan0 link"
        result = sta.cmd(cmd)
        
        for line in result.split('\n'):
            if 'signal:' in line:
                match = re.search(r'signal:\s*([-\d]+)', line)
                if match:
                    return match.group(1).strip()
        
        cmd = f"iwconfig {sta_name}-wlan0 | grep -i quality"
        result = sta.cmd(cmd)
        for line in result.split('\n'):
            if 'signal level' in line.lower():
                match = re.search(r'signal level[=:]\s*([-\d]+)', line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        return '-100'
    except Exception as e:
        info(f"Erro ao obter RSSI: {e}\n")
        return '-100'

def obter_latencia(sta):
    """Obtém a latência de forma mais robusta"""
    try:
        ping_result = sta.cmd('ping -c 1 -W 2 10.0.0.1')
        
        for line in ping_result.split('\n'):
            if 'time=' in line:
                match = re.search(r'time=([\d.]+)', line)
                if match:
                    return match.group(1)
        
        ping_result = sta.cmd('ping -c 1 -W 2 8.8.8.8')
        for line in ping_result.split('\n'):
            if 'time=' in line:
                match = re.search(r'time=([\d.]+)', line)
                if match:
                    return match.group(1)
        
        return '9999'
    except Exception as e:
        info(f"Erro ao obter latência: {e}\n")
        return '9999'

def obter_ap_especifico(sta, sta_name, ap_objs):
    """Obtém qual AP específico a station está conectada"""
    try:
        # Primeiro verificar se está conectado
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

def obter_links_ap_melhorado(net, ap_objs):
    """Obtém links entre APs de forma mais precisa"""
    links = []
    try:
        # Usar ovs-vsctl para obter todas as bridges
        cmd = "ovs-vsctl list-br"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            bridges = result.stdout.strip().split('\n')
            
            for bridge in bridges:
                if bridge and bridge in ap_objs:
                    # Obter portas da bridge
                    cmd = f"ovs-vsctl list-ports {bridge}"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        ports = result.stdout.strip().split('\n')
                        for port in ports:
                            if port and port != bridge:
                                # Verificar se é link para outro AP
                                for other_ap in ap_objs.keys():
                                    if other_ap in port and other_ap != bridge:
                                        links.append({
                                            'from': bridge,
                                            'to': other_ap,
                                            'port': port,
                                            'type': 'mesh_link'
                                        })
        
        # Se não encontrou links mesh, verificar se há conectividade entre APs
        if not links:
            for ap1_name in ap_objs.keys():
                for ap2_name in ap_objs.keys():
                    if ap1_name != ap2_name:
                        # Tentar ping entre APs
                        try:
                            ap1 = ap_objs[ap1_name]
                            ap2 = ap_objs[ap2_name]
                            
                            # Verificar se há rota entre eles
                            cmd = f"ip route get 10.0.0.{list(ap_objs.keys()).index(ap2_name) + 1}"
                            result = ap1.cmd(cmd)
                            
                            if 'via' in result or 'dev' in result:
                                links.append({
                                    'from': ap1_name,
                                    'to': ap2_name,
                                    'port': 'route',
                                    'type': 'network_route'
                                })
                        except:
                            continue
                            
    except Exception as e:
        info(f"Erro ao obter links AP: {e}\n")
    
    return links

def obter_estado_mesh(net, ap_objs):
    """Obtém estado detalhado da rede mesh"""
    estado = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'total_aps': len(ap_objs),
        'aps_ativos': 0,
        'links_mesh': 0,
        'controller_status': 'unknown'
    }
    
    try:
        # Verificar APs ativos
        for ap_name, ap in ap_objs.items():
            try:
                # Verificar se o AP está respondendo
                result = ap.cmd('echo "test"')
                if result.strip() == 'test':
                    estado['aps_ativos'] += 1
            except:
                continue
        
        # Verificar controller
        try:
            cmd = "ovs-vsctl show | grep -i controller"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and 'is_connected: true' in result.stdout:
                estado['controller_status'] = 'connected'
            else:
                estado['controller_status'] = 'disconnected'
        except:
            estado['controller_status'] = 'error'
            
    except Exception as e:
        info(f"Erro ao obter estado mesh: {e}\n")
    
    return estado

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

def executar_simulacao_mesh_v2(config):
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

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

    # Log de topologia mesh inicial
    os.makedirs('results', exist_ok=True)
    
    # Log de links entre APs
    mesh_log_path = os.path.join('results', 'mesh_topology_v2.csv')
    with open(mesh_log_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['time', 'total_aps', 'aps_ativos', 'links_mesh', 'controller_status', 'links_detalhados']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Log inicial da topologia
        links = obter_links_ap_melhorado(net, ap_objs)
        estado = obter_estado_mesh(net, ap_objs)
        
        writer.writerow({
            'time': estado['timestamp'],
            'total_aps': estado['total_aps'],
            'aps_ativos': estado['aps_ativos'],
            'links_mesh': len(links),
            'controller_status': estado['controller_status'],
            'links_detalhados': str(links)
        })

    info("*** Movimentando stations\n")
    for sta_conf in config["stations"]:
        sta = sta_objs[sta_conf["name"]]
        log_file = f'{sta_conf["name"]}_mesh_v2_log.csv'
        log_path = os.path.join('results', log_file)
        
        with open(log_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['time', 'position', 'rssi', 'latency_ms', 'ap_conectado', 'aps_visiveis']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Log da posição inicial
            rssi = obter_rssi(sta, sta_conf["name"])
            latency = obter_latencia(sta)
            ap_conectado = obter_ap_especifico(sta, sta_conf["name"], ap_objs)
            aps_visiveis = scan_wifi_completo(sta, sta_conf["name"])
            
            writer.writerow({
                'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'position': f'{sta_conf["start_x"]},{sta_conf["start_y"]}',
                'rssi': rssi,
                'latency_ms': latency,
                'ap_conectado': ap_conectado,
                'aps_visiveis': aps_visiveis
            })
            info(f"{sta_conf['name']} → pos=({sta_conf['start_x']},{sta_conf['start_y']}) RSSI={rssi} latency={latency} AP={ap_conectado} Scan={aps_visiveis}\n")

            # Mover pelas trajetórias
            for point in sta_conf["trajectory"]:
                x, y = point
                sta.setPosition(f'{x},{y},0')
                time.sleep(config.get("wait", 2))

                rssi = obter_rssi(sta, sta_conf["name"])
                latency = obter_latencia(sta)
                ap_conectado = obter_ap_especifico(sta, sta_conf["name"], ap_objs)
                aps_visiveis = scan_wifi_completo(sta, sta_conf["name"])

                writer.writerow({
                    'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'position': f'{x},{y}',
                    'rssi': rssi,
                    'latency_ms': latency,
                    'ap_conectado': ap_conectado,
                    'aps_visiveis': aps_visiveis
                })
                info(f"{sta_conf['name']} → pos=({x},{y}) RSSI={rssi} latency={latency} AP={ap_conectado} Scan={aps_visiveis}\n")

    info("*** Encerrando rede\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    if len(sys.argv) < 2:
        print("Uso: python3 executa_cenario_mesh_v2.py cenario.json")
        sys.exit(1)
    conf = carregar_config(sys.argv[1])
    executar_simulacao_mesh_v2(conf) 