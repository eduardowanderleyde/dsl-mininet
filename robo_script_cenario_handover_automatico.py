#!/usr/bin/env python3
"""
Script para robô real - Cenário: cenario_handover_automatico.json
Executa movimento e coleta dados WiFi reais
"""

import time
import json
import csv
import subprocess
import serial
import math
from datetime import datetime

# Configurações do robô
ROBO_CONFIG = {
    "serial_port": "/dev/ttyUSB0",  # Porta serial do robô
    "baudrate": 9600,
    "wifi_interface": "wlan0",
    "movement_speed": 2.0,
    "sampling_interval": 1.0
}

# Configurações do cenário
CENARIO_CONFIG = {
  "ssid": "meshNet",
  "channel": 1,
  "wait": 3,
  "handover": {
    "enabled": true,
    "threshold": -65,
    "hysteresis": 5
  },
  "aps": [
    {
      "name": "ap1",
      "x": 10.0,
      "y": 20.0,
      "range": 25,
      "channel": 1
    },
    {
      "name": "ap2",
      "x": 30.0,
      "y": 20.0,
      "range": 25,
      "channel": 1
    },
    {
      "name": "ap3",
      "x": 50.0,
      "y": 20.0,
      "range": 25,
      "channel": 1
    }
  ],
  "stations": [
    {
      "name": "sta1",
      "start_x": 5.0,
      "start_y": 20.0,
      "trajectory": [
        [
          15.0,
          20.0
        ],
        [
          25.0,
          20.0
        ],
        [
          35.0,
          20.0
        ],
        [
          45.0,
          20.0
        ],
        [
          55.0,
          20.0
        ]
      ]
    }
  ]
}

def conectar_robo():
    """Conecta com o robô via serial"""
    try:
        ser = serial.Serial(ROBO_CONFIG["serial_port"], ROBO_CONFIG["baudrate"], timeout=1)
        print(f"✅ Conectado ao robô em {ROBO_CONFIG['serial_port']}")
        return ser
    except Exception as e:
        print(f"❌ Erro ao conectar com robô: {e}")
        return None

def enviar_comando_robo(ser, comando):
    """Envia comando para o robô"""
    try:
        ser.write(f"{comando}\n".encode())
        time.sleep(0.1)
        resposta = ser.readline().decode().strip()
        return resposta
    except Exception as e:
        print(f"❌ Erro ao enviar comando: {e}")
        return None

def obter_dados_wifi():
    """Obtém dados WiFi reais"""
    try:
        # RSSI
        cmd_rssi = f"iw dev {ROBO_CONFIG['wifi_interface']} link"
        result_rssi = subprocess.run(cmd_rssi, shell=True, capture_output=True, text=True)
        
        # Latência
        cmd_ping = "ping -c 1 -W 2 8.8.8.8"
        result_ping = subprocess.run(cmd_ping, shell=True, capture_output=True, text=True)
        
        # SSID atual
        cmd_ssid = f"iw dev {ROBO_CONFIG['wifi_interface']} link | grep SSID"
        result_ssid = subprocess.run(cmd_ssid, shell=True, capture_output=True, text=True)
        
        rssi = -100
        latency = 9999
        ssid = "N/A"
        
        # Parse RSSI
        for line in result_rssi.stdout.split('\n'):
            if 'signal:' in line:
                try:
                    rssi = int(line.split('signal:')[1].split()[0])
                except:
                    pass
        
        # Parse latência
        for line in result_ping.stdout.split('\n'):
            if 'time=' in line:
                try:
                    latency = float(line.split('time=')[1].split()[0])
                except:
                    pass
        
        # Parse SSID
        if result_ssid.stdout.strip():
            ssid = result_ssid.stdout.strip().split('SSID:')[1].strip()
        
        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'rssi': rssi,
            'latency': latency,
            'ssid': ssid,
            'position': [0, 0]  # Será atualizado pelo robô
        }
        
    except Exception as e:
        print(f"❌ Erro ao obter dados WiFi: {e}")
        return None

def mover_robo(ser, x, y):
    """Move o robô para posição (x, y)"""
    comando = f"MOVE {x} {y}"
    resposta = enviar_comando_robo(ser, comando)
    print(f"🤖 Movendo para ({x}, {y}): {resposta}")
    return resposta

def executar_cenario_robo():
    """Executa o cenário no robô real"""
    print("🚀 Iniciando execução no robô real...")
    
    # Conectar com robô
    ser = conectar_robo()
    if not ser:
        print("❌ Não foi possível conectar com o robô")
        return
    
    try:
        # Criar arquivo de log
        log_file = f'robo_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        with open(log_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'x', 'y', 'rssi', 'latency', 'ssid', 'handover']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Posição inicial
            pos_atual = [0, 0]
            ssid_anterior = None
            
            # Executar para cada station
            for station in CENARIO_CONFIG.get('stations', []):
                print(f"📱 Executando station: {station['name']}")
                
                # Posição inicial da station
                pos_atual = [station['start_x'], station['start_y']]
                mover_robo(ser, pos_atual[0], pos_atual[1])
                time.sleep(2)
                
                # Dados iniciais
                dados = obter_dados_wifi()
                if dados:
                    dados['x'] = pos_atual[0]
                    dados['y'] = pos_atual[1]
                    dados['handover'] = False
                    writer.writerow(dados)
                    print(f"📊 Dados iniciais: {dados}")
                
                # Mover pela trajetória
                for i, ponto in enumerate(station['trajectory']):
                    x_dest, y_dest = ponto
                    
                    print(f"🚗 Movendo para ({x_dest}, {y_dest})")
                    
                    # Mover robô
                    mover_robo(ser, x_dest, y_dest)
                    pos_atual = [x_dest, y_dest]
                    
                    # Aguardar estabilização
                    time.sleep(ROBO_CONFIG['sampling_interval'])
                    
                    # Coletar dados
                    dados = obter_dados_wifi()
                    if dados:
                        dados['x'] = pos_atual[0]
                        dados['y'] = pos_atual[1]
                        
                        # Detectar handover
                        if ssid_anterior and dados['ssid'] != ssid_anterior:
                            dados['handover'] = True
                            print(f"🔄 Handover detectado: {ssid_anterior} → {dados['ssid']}")
                        else:
                            dados['handover'] = False
                        
                        writer.writerow(dados)
                        print(f"📊 Dados: {dados}")
                        
                        ssid_anterior = dados['ssid']
        
        print(f"✅ Execução concluída! Log salvo em: {log_file}")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
    
    finally:
        ser.close()

if __name__ == "__main__":
    executar_cenario_robo()
