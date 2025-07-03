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
        # Método 1: Tentar obter informações da conexão atual
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
        
        # Método 2: Se não encontrou, tentar scan completo
        if ssid == 'N/A' or bssid == 'N/A':
            info(f"   🔍 Executando scan WiFi para {sta_name}...\n")
            scan_result = sta.cmd(f'iw dev {sta_name}-wlan0 scan')
            
            for line in scan_result.split('\n'):
                if 'SSID:' in line and ssid == 'N/A':
                    ssid = line.split('SSID:')[1].strip()
                    if ssid:  # Se não for vazio
                        info(f"   📶 SSID encontrado: {ssid}\n")
                elif 'BSS' in line and bssid == 'N/A':
                    parts = line.split()
                    if len(parts) > 1:
                        bssid = parts[1]
                        info(f"   📡 BSSID encontrado: {bssid}\n")
        
        # Método 3: Tentar obter via iwconfig (fallback)
        if ssid == 'N/A':
            try:
                iwconfig_result = sta.cmd(f'iwconfig {sta_name}-wlan0')
                for line in iwconfig_result.split('\n'):
                    if 'ESSID:' in line:
                        match = re.search(r'ESSID:"([^"]*)"', line)
                        if match:
                            ssid = match.group(1)
                            info(f"   📶 SSID via iwconfig: {ssid}\n")
                            break
            except:
                pass
        
        return {
            'SSID': ssid,
            'BSSID': bssid,
            'Signal Level (dBm)': rssi
        }
        
    except Exception as e:
        info(f"   ❌ Erro ao obter info WiFi: {e}\n")
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

def obter_rssi(sta, iface_name):
    """Obtém RSSI atual da interface"""
    try:
        result = sta.cmd(f"iw dev {iface_name} link")
        for line in result.split('\n'):
            if "signal:" in line:
                rssi = int(line.split('signal:')[1].split()[0])
                return rssi
        return -100
    except Exception as e:
        info(f"   ❌ Erro ao obter RSSI: {e}\n")
        return -100

def verificar_melhor_ap(sta, iface_name, threshold=-65):
    """Verifica se existe AP com sinal melhor que o threshold"""
    try:
        result = sta.cmd(f"iw dev {iface_name} scan")
        melhor_ap = None
        melhor_rssi = -100

        current_bss = None
        rssi = -100

        for line in result.split('\n'):
            line = line.strip()

            if line.startswith("BSS"):
                current_bss = line.split()[1]

            if "signal:" in line:
                try:
                    rssi = int(float(line.split('signal:')[1].split()[0]))
                except:
                    rssi = -100

            if "SSID:" in line:
                ssid = line.split("SSID:")[1].strip()
                if rssi > melhor_rssi and rssi > threshold:
                    melhor_ap = ssid
                    melhor_rssi = rssi

        return melhor_ap, melhor_rssi
    except Exception as e:
        info(f"   ❌ Erro ao verificar melhor AP: {e}\n")
        return None, -100

def forcar_handover(sta, iface_name, novo_ssid):
    """Força handover para novo AP"""
    try:
        info(f"   🔄 Desconectando da rede atual...\n")
        sta.cmd(f"iw dev {iface_name} disconnect")
        time.sleep(1)

        info(f"   🔄 Conectando ao novo AP: {novo_ssid}\n")
        sta.cmd(f"iw dev {iface_name} connect {novo_ssid}")
        time.sleep(2)
        
        return True
    except Exception as e:
        info(f"   ❌ Erro ao forçar handover: {e}\n")
        return False

def monitorar_e_forcar_handover(sta, sta_name, threshold=-65, hysteresis=5):
    """Monitora e força handover quando necessário"""
    try:
        iface_name = f"{sta_name}-wlan0"
        atual_rssi = obter_rssi(sta, iface_name)
        melhor_ap, melhor_rssi = verificar_melhor_ap(sta, iface_name, threshold)

        if melhor_ap and melhor_rssi > atual_rssi + hysteresis:
            info(f"   🎯 Melhor AP encontrado: {melhor_ap} ({melhor_rssi} dBm), atual: {atual_rssi} dBm → Forçando handover!\n")
            if forcar_handover(sta, iface_name, melhor_ap):
                return {
                    'handover': True,
                    'new_bssid': melhor_ap,
                    'old_rssi': atual_rssi,
                    'new_rssi': melhor_rssi,
                    'reason': 'melhor_sinal'
                }
        else:
            info(f"   📊 Sem necessidade de handover. Atual: {atual_rssi} dBm, Melhor: {melhor_rssi} dBm\n")
        
        return {'handover': False}
        
    except Exception as e:
        info(f"   ❌ Erro no monitoramento de handover: {e}\n")
        return {'handover': False}

def detectar_handover(sta, sta_name, ap_objs, ap_anterior):
    """Detecta handover entre APs (método original mantido para compatibilidade)"""
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

def calcular_posicao_intermediaria(pos_atual, pos_destino, velocidade, tempo_total):
    """Calcula posição intermediária para movimento contínuo"""
    x1, y1 = pos_atual
    x2, y2 = pos_destino
    
    # Calcular distância total
    distancia = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    if distancia == 0:
        return pos_atual
    
    # Calcular tempo necessário para percorrer a distância
    tempo_necessario = distancia / velocidade
    
    # Calcular progresso (0 a 1)
    progresso = min(tempo_total / tempo_necessario, 1.0)
    
    # Calcular posição intermediária
    x_inter = x1 + (x2 - x1) * progresso
    y_inter = y1 + (y2 - y1) * progresso
    
    return [x_inter, y_inter]

def aplicar_modelo_propagacao(rssi_base, distancia, modelo="simple"):
    """Aplica diferentes modelos de propagação de sinal"""
    import math
    import random
    
    if modelo == "simple":
        # Modelo simples: atenuação linear com distância
        return rssi_base - (distancia * 0.5)
    
    elif modelo == "log_distance":
        # Modelo log-distance: atenuação logarítmica
        if distancia <= 1:
            return rssi_base
        return rssi_base - (20 * math.log10(distancia))
    
    elif modelo == "friis":
        # Modelo Friis: propagação em espaço livre
        if distancia <= 1:
            return rssi_base
        return rssi_base - (20 * math.log10(distancia) + 20 * math.log10(2.4e9) + 147.55)
    
    elif modelo == "two_ray_ground":
        # Modelo Two-Ray Ground: considera reflexão no solo
        if distancia <= 1:
            return rssi_base
        h_tx = 1.5  # Altura da antena transmissora (m)
        h_rx = 1.5  # Altura da antena receptora (m)
        d_cross = (4 * math.pi * h_tx * h_rx) / 0.125  # Distância de cruzamento (m)
        
        if distancia < d_cross:
            return rssi_base - (20 * math.log10(distancia))
        else:
            return rssi_base - (40 * math.log10(distancia) - 20 * math.log10(h_tx * h_rx))
    
    elif modelo == "shadowing":
        # Modelo com shadowing: adiciona variação aleatória
        shadowing_std = 4  # Desvio padrão do shadowing (dB)
        rssi_log_distance = rssi_base - (20 * math.log10(max(distancia, 1)))
        shadowing = random.gauss(0, shadowing_std)
        return rssi_log_distance + shadowing
    
    else:
        return rssi_base - (distancia * 0.5)  # Fallback para modelo simples

def executar_simulacao_mesh_v4(config):
    """Executa simulação mesh com coleta completa de dados e handover automático"""
    
    info("*** 🚀 Iniciando DSL Mininet-WiFi v4.0 SUPER COMPLETA COM HANDOVER AUTOMÁTICO\n")
    
    # Configurações de handover automático
    handover_config = config.get("handover", {})
    threshold = handover_config.get("threshold", -65)  # dBm
    hysteresis = handover_config.get("hysteresis", 5)  # dBm
    auto_handover = handover_config.get("enabled", True)
    
    # Configurações de propagação e mobilidade
    propagation_config = config.get("propagation", {})
    propagation_model = propagation_config.get("model", "simple")
    mobility_type = propagation_config.get("mobility_type", "discrete")
    mobility_speed = propagation_config.get("mobility_speed", 2.0)
    sampling_interval = propagation_config.get("sampling_interval", 1.0)
    
    info(f"*** ⚙️ Configurações de Handover: Threshold={threshold}dBm, Histerese={hysteresis}dBm, Ativo={auto_handover}\n")
    info(f"*** 📡 Modelo de Propagação: {propagation_model}\n")
    info(f"*** 🚗 Tipo de Mobilidade: {mobility_type}, Velocidade: {mobility_speed}m/s\n")
    
    # Criar rede
    net = Mininet_wifi(controller=Controller)
    
    # Adicionar controller
    info("*** Adicionando controller\n")
    c0 = net.addController('c0', controller=Controller, ip='127.0.0.1', port=6633)
    
    # Adicionar APs
    info("*** Adicionando APs\n")
    ap_objs = {}
    ssid_global = config.get("ssid", "meshNet")  # SSID global do cenário
    for ap_conf in config["aps"]:
        ap = net.addAccessPoint(
            ap_conf["name"], 
            ssid=ssid_global,  # Usar SSID global
            mode="g", 
            channel=config.get("channel", 1),  # Canal global
            position=f'{ap_conf["x"]},{ap_conf["y"]},0',
            range=ap_conf.get("range", 30)
        )
        ap_objs[ap_conf["name"]] = ap
        info(f"   📡 AP {ap_conf['name']} em ({ap_conf['x']}, {ap_conf['y']}) - SSID: {ssid_global}\n")
    
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
            pos_atual = [sta_conf["start_x"], sta_conf["start_y"]]
            
            for i, point in enumerate(sta_conf["trajectory"]):
                x_destino, y_destino = point
                
                if mobility_type == "discrete":
                    # Movimento discreto (saltos) - comportamento original
                    info(f"   🚗 Movendo para ({x_destino}, {y_destino})\n")
                    sta.setPosition(f'{x_destino},{y_destino},0')
                    time.sleep(config.get("wait", 3))
                    
                    # Coletar dados uma vez no ponto de destino
                    wifi_info = obter_info_wifi_detalhada(sta, sta_conf["name"])
                    latency_info = obter_latencia_completa(sta)
                    bandwidth_info = obter_bandwidth_iperf3(sta)
                    
                    # Aplicar modelo de propagação se necessário
                    if propagation_model != "simple":
                        # Calcular distância para APs próximos e ajustar RSSI
                        for ap_name, ap in ap_objs.items():
                            ap_pos = [ap_conf["x"], ap_conf["y"]]
                            distancia = ((x_destino - ap_pos[0]) ** 2 + (y_destino - ap_pos[1]) ** 2) ** 0.5
                            if distancia <= ap_conf.get("range", 30):
                                # Aplicar modelo de propagação
                                rssi_ajustado = aplicar_modelo_propagacao(-30, distancia, propagation_model)
                                info(f"   📡 RSSI ajustado para {ap_name}: {rssi_ajustado:.1f} dBm (modelo: {propagation_model})\n")
                    
                elif mobility_type == "continuous":
                    # Movimento contínuo (suave)
                    info(f"   🚗 Movimento contínuo para ({x_destino}, {y_destino})\n")
                    
                    # Calcular tempo total para o movimento
                    distancia_total = ((x_destino - pos_atual[0]) ** 2 + (y_destino - pos_atual[1]) ** 2) ** 0.5
                    tempo_total = distancia_total / mobility_speed
                    
                    # Dividir movimento em pequenos passos
                    num_passos = max(1, int(tempo_total / sampling_interval))
                    tempo_por_passo = tempo_total / num_passos
                    
                    for passo in range(num_passos + 1):
                        # Calcular posição intermediária
                        progresso = passo / num_passos
                        x_inter = pos_atual[0] + (x_destino - pos_atual[0]) * progresso
                        y_inter = pos_atual[1] + (y_destino - pos_atual[1]) * progresso
                        
                        # Mover para posição intermediária
                        sta.setPosition(f'{x_inter},{y_inter},0')
                        time.sleep(sampling_interval)
                        
                        # Coletar dados em cada passo
                        wifi_info = obter_info_wifi_detalhada(sta, sta_conf["name"])
                        latency_info = obter_latencia_completa(sta)
                        bandwidth_info = obter_bandwidth_iperf3(sta)
                        
                        # Aplicar modelo de propagação
                        if propagation_model != "simple":
                            for ap_name, ap in ap_objs.items():
                                ap_pos = [ap_conf["x"], ap_conf["y"]]
                                distancia = ((x_inter - ap_pos[0]) ** 2 + (y_inter - ap_pos[1]) ** 2) ** 0.5
                                if distancia <= ap_conf.get("range", 30):
                                    rssi_ajustado = aplicar_modelo_propagacao(-30, distancia, propagation_model)
                                    if passo % 5 == 0:  # Log a cada 5 passos para não poluir
                                        info(f"   📡 Pos({x_inter:.1f},{y_inter:.1f}) -> {ap_name}: {rssi_ajustado:.1f} dBm\n")
                        
                        # Handover automático ou detecção manual
                        if auto_handover:
                            handover_info = monitorar_e_forcar_handover(sta, sta_conf["name"], threshold, hysteresis)
                        else:
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
                        
                        # Escrever dados no log
                        writer.writerow({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'wifi_info': str([wifi_info]),
                            'latency_info': str(latency_info),
                            'bandwidth_info': str(bandwidth_info),
                            'handover_info': str(handover_info)
                        })
                        
                        if passo % 10 == 0:  # Log a cada 10 passos
                            info(f"   📊 Passo {passo}/{num_passos}: {wifi_info} | {latency_info} | {bandwidth_info} | {handover_info}\n")
                    
                    # Atualizar posição atual
                    pos_atual = [x_destino, y_destino]
                
                elif mobility_type == "random_walk":
                    # Movimento aleatório (random walk)
                    info(f"   🎲 Random walk para ({x_destino}, {y_destino})\n")
                    
                    # Gerar pontos intermediários aleatórios
                    num_pontos = max(3, int(distancia_total / 5))  # Um ponto a cada 5 metros
                    pontos_intermediarios = []
                    
                    for _ in range(num_pontos - 1):
                        # Gerar ponto aleatório entre pos_atual e destino
                        t = random.random()
                        x_rand = pos_atual[0] + (x_destino - pos_atual[0]) * t + random.uniform(-2, 2)
                        y_rand = pos_atual[1] + (y_destino - pos_atual[1]) * t + random.uniform(-2, 2)
                        pontos_intermediarios.append([x_rand, y_rand])
                    
                    # Adicionar destino final
                    pontos_intermediarios.append([x_destino, y_destino])
                    
                    # Mover pelos pontos intermediários
                    for ponto in pontos_intermediarios:
                        x_inter, y_inter = ponto
                        sta.setPosition(f'{x_inter},{y_inter},0')
                        time.sleep(sampling_interval)
                        
                        # Coletar dados
                        wifi_info = obter_info_wifi_detalhada(sta, sta_conf["name"])
                        latency_info = obter_latencia_completa(sta)
                        bandwidth_info = obter_bandwidth_iperf3(sta)
                        
                        # Handover automático ou detecção manual
                        if auto_handover:
                            handover_info = monitorar_e_forcar_handover(sta, sta_conf["name"], threshold, hysteresis)
                        else:
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
                        
                        # Escrever dados no log
                        writer.writerow({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'wifi_info': str([wifi_info]),
                            'latency_info': str(latency_info),
                            'bandwidth_info': str(bandwidth_info),
                            'handover_info': str(handover_info)
                        })
                        
                        info(f"   📊 Random walk: ({x_inter:.1f},{y_inter:.1f}) | {wifi_info} | {latency_info} | {bandwidth_info} | {handover_info}\n")
                    
                    # Atualizar posição atual
                    pos_atual = [x_destino, y_destino]
                
                # Para movimento discreto, continuar com o código original
                if mobility_type == "discrete":
                    # Coletar dados completos
                    wifi_info = obter_info_wifi_detalhada(sta, sta_conf["name"])
                    latency_info = obter_latencia_completa(sta)
                    bandwidth_info = obter_bandwidth_iperf3(sta)
                    
                    # Handover automático ou detecção manual
                    if auto_handover:
                        handover_info = monitorar_e_forcar_handover(sta, sta_conf["name"], threshold, hysteresis)
                    else:
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
