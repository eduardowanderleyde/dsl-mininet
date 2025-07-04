import os
import json
import subprocess
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import paramiko
from logger_config import robo_logger
from raspberry_connection import raspberry_conn, RaspberryConnection

app = Flask(__name__)
app.secret_key = 'segredo-super-simples'
CENARIOS_DIR = 'cenarios'

# Configurações SSH para execução remota
SSH_HOST = '192.168.68.106'
SSH_USER = 'eduardo-wanderley'
SSH_KEY = '/home/eduardo-wanderley/.ssh/id_rsa'
REMOTE_PATH = '/home/eduardo-wanderley/Desktop/dsl-mininet'

os.makedirs(CENARIOS_DIR, exist_ok=True)

@app.route('/')
def index():
    cenarios = [f for f in os.listdir(CENARIOS_DIR) if f.endswith('.json')]
    return render_template('index.html', cenarios=cenarios)

@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        ssid = request.form.get('ssid', 'meshNet')
        channel = int(request.form.get('channel', 1))
        wait = int(request.form.get('wait', 2))
        ap_range = int(request.form.get('ap_range', 30))
        
        # Configurações de handover automático
        handover_enabled = request.form.get('handover_enabled', 'true') == 'true'
        handover_threshold = int(request.form.get('handover_threshold', -65))
        handover_hysteresis = int(request.form.get('handover_hysteresis', 5))
        
        # Configurações avançadas de propagação e mobilidade
        propagation_model = request.form.get('propagation_model', 'simple')
        mobility_type = request.form.get('mobility_type', 'discrete')
        mobility_speed = float(request.form.get('mobility_speed', 2.0))
        sampling_interval = float(request.form.get('sampling_interval', 1.0))
        
        # APs
        ap_names = request.form.getlist('ap_name')
        ap_xs = request.form.getlist('ap_x')
        ap_ys = request.form.getlist('ap_y')
        ap_ranges = request.form.getlist('ap_range')
        ap_channels = request.form.getlist('ap_channel')
        aps = []
        for n, x, y, r, c in zip(ap_names, ap_xs, ap_ys, ap_ranges, ap_channels):
            if n.strip() != '':
                aps.append({
                    "name": n.strip(), 
                    "x": float(x), 
                    "y": float(y),
                    "range": int(r) if r else ap_range,
                    "channel": int(c) if c else channel
                })
        
        # Stations
        sta_names = request.form.getlist('sta_name')
        sta_start_xs = request.form.getlist('sta_start_x')
        sta_start_ys = request.form.getlist('sta_start_y')
        sta_trajs = request.form.getlist('sta_traj')
        stations = []
        for n, x, y, traj in zip(sta_names, sta_start_xs, sta_start_ys, sta_trajs):
            if n.strip() != '':
                # Trajetória: string "10,10;20,20" -> lista de listas
                traj_list = []
                for p in traj.split(';'):
                    p = p.strip()
                    if p:
                        px, py = p.split(',')
                        traj_list.append([float(px), float(py)])
                stations.append({
                    "name": n.strip(),
                    "start_x": float(x),
                    "start_y": float(y),
                    "trajectory": traj_list
                })
        
        config = {
            "ssid": ssid,
            "channel": channel,
            "wait": wait,
            "aps": aps,
            "stations": stations,
            "handover": {
                "enabled": handover_enabled,
                "threshold": handover_threshold,
                "hysteresis": handover_hysteresis
            },
            "propagation": {
                "model": propagation_model,
                "mobility_type": mobility_type,
                "mobility_speed": mobility_speed,
                "sampling_interval": sampling_interval
            }
        }
        nome = f"cenario_{ssid}_{len(os.listdir(CENARIOS_DIR))}.json"
        with open(os.path.join(CENARIOS_DIR, nome), 'w') as f:
            json.dump(config, f, indent=2)
        flash(f'Cenário salvo como {nome}!', 'success')
        return redirect(url_for('index'))
    return render_template('form.html', aps=[], stations=[], ssid='meshNet', channel=1, wait=2)

@app.route('/preview/<nome>')
def preview(nome):
    caminho = os.path.join(CENARIOS_DIR, nome)
    if not os.path.exists(caminho):
        flash('Cenário não encontrado!', 'danger')
        return redirect(url_for('index'))
    with open(caminho) as f:
        config = json.load(f)
    return render_template('preview.html', config=config)

@app.route('/download/<nome>')
def download(nome):
    return send_from_directory(CENARIOS_DIR, nome, as_attachment=True)

@app.route('/logs')
def logs():
    """Lista todos os logs disponíveis na pasta results"""
    if not os.path.exists('results'):
        os.makedirs('results', exist_ok=True)
    logs = [f for f in os.listdir('results') if f.endswith(('.csv', '.log'))]
    return render_template('logs.html', logs=logs)

@app.route('/download_log/<nome>')
def download_log(nome):
    """Baixa um arquivo de log específico"""
    return send_from_directory('results', nome, as_attachment=True)

@app.route('/view_log/<nome>')
def view_log(nome):
    """Visualiza o conteúdo de um arquivo de log"""
    caminho = os.path.join('results', nome)
    if not os.path.exists(caminho):
        flash('Arquivo de log não encontrado!', 'danger')
        return redirect(url_for('logs'))
    
    try:
        with open(caminho, 'r') as f:
            conteudo = f.read()
        return render_template('view_log.html', nome=nome, conteudo=conteudo)
    except Exception as e:
        flash(f'Erro ao ler arquivo: {e}', 'danger')
        return redirect(url_for('logs'))

@app.route('/tutorial')
def tutorial():
    """Página de tutorial completo do DSL Mininet-WiFi v4.0"""
    return render_template('tutorial.html')

@app.route('/limpar_arquivos_antigos')
def limpar_arquivos_antigos():
    """Remove arquivos antigos e desnecessários"""
    arquivos_para_remover = [
        # Scripts antigos (funcionalidade integrada na v4.0)
        'executa_cenario_mesh_v2.py',
        'executa_cenario_mesh_v3.py',
        'executa_cenario_scan_wifi.py',
        'executa_raspberry_movel.py',
        'executa_cenario_handover_forcado.py',
        'executa_cenario_mesh.py',
        'executa_cenario.py',
        
        # Scripts de teste (não mais necessários)
        'teste_novas_ferramentas.py',
        'teste_todos_cenarios.py',
        'teste_limites_conectividade.py',
        'teste_manual_incremental.py',
        'teste_cenarios.py',
        
        # Scripts de análise (funcionalidade integrada)
        'analisador_performance_avancado.py',
        'analisar_raspberry_pi.py',
        'analisar_mesh.py',
        'analisar_logs.py',
        'gerador_relatorios.py',
        
        # Documentação antiga (redundante)
        'SUGESTOES_MELHORIAS_FERRAMENTAS.md',
        'ESTADO_ATUAL_CENARIOS.md',
        'MELHORIAS_IMPLEMENTADAS_V3.md',
        'ANALISE_FUNCOES_MELHORIAS.md',
        'CORRECOES_NOMES_STATIONS.md',
        'RESUMO_DESCOBERTAS.md',
        'DOCUMENTACAO_TESTES.md',
        'RELATORIO_LIMITES_CONECTIVIDADE.md',
        'IMPLEMENTACAO_MESH_MONITORING.md',
        'DOCUMENTACAO_COMPLETA.md',
        
        # Arquivos temporários e antigos
        '1.txt',
        'station1_log.csv',
        'cenario_meshNet_1.json',
        'cenario_exemplo_3.json',
        'Dockerfile'
    ]
    
    arquivos_removidos = []
    for arquivo in arquivos_para_remover:
        if os.path.exists(arquivo):
            try:
                os.remove(arquivo)
                arquivos_removidos.append(arquivo)
            except Exception as e:
                print(f"Erro ao remover {arquivo}: {e}")
    
    # Limpar logs antigos em results/
    if os.path.exists('results'):
        logs_antigos = [
            'sta1_metrics.csv', 'sta2_metrics.csv', 'sta1_mesh_v2_log.csv',
            'mesh_topology_v2.csv', 'mobile_sta_mesh_v2_log.csv',
            'raspberrypi_mesh_v2_log.csv', 'raspberry_pi_mesh_v2_log.csv',
            'sta2_mesh_v2_log.csv', 'sta1_mesh_log.csv', 'mesh_topology.csv',
            'sta1_log.csv', 'sta2_log.csv', 'handover_events.csv',
            'network_metrics.csv', 'complete_logs.json'
        ]
        
        for log in logs_antigos:
            log_path = os.path.join('results', log)
            if os.path.exists(log_path):
                try:
                    os.remove(log_path)
                    arquivos_removidos.append(f"results/{log}")
                except Exception as e:
                    print(f"Erro ao remover {log}: {e}")
    
    # Limpar pasta cenarios_novos se existir
    if os.path.exists('cenarios_novos'):
        try:
            import shutil
            # Mover cenários úteis para a pasta principal
            cenarios_novos = os.listdir('cenarios_novos')
            for cenario in cenarios_novos:
                if cenario.endswith('.json'):
                    origem = os.path.join('cenarios_novos', cenario)
                    destino = os.path.join('cenarios', cenario)
                    if not os.path.exists(destino):  # Só move se não existir
                        shutil.move(origem, destino)
                        arquivos_removidos.append(f"Movido: {cenario}")
            
            # Remover pasta cenarios_novos se vazia
            if not os.listdir('cenarios_novos'):
                shutil.rmtree('cenarios_novos')
                arquivos_removidos.append("Pasta cenarios_novos removida")
        except Exception as e:
            print(f"Erro ao processar cenarios_novos: {e}")
    
    flash(f'Limpeza concluída! {len(arquivos_removidos)} arquivos processados.', 'success')
    return redirect(url_for('index'))

def executar_remoto(nome_arquivo_local, nome_arquivo_remoto):
    print(f"[LOG] Iniciando execução remota...")
    print(f"[LOG] Conectando em {SSH_HOST} como {SSH_USER} usando chave {SSH_KEY}")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, key_filename=SSH_KEY)
        print("[LOG] Conexão SSH estabelecida.")
    except Exception as e:
        print(f"[ERRO] Falha ao conectar via SSH: {e}")
        raise
    try:
        sftp = ssh.open_sftp()
        print(f"[LOG] Enviando arquivo {nome_arquivo_local} para {REMOTE_PATH}/{nome_arquivo_remoto}")
        sftp.put(nome_arquivo_local, f"{REMOTE_PATH}/{nome_arquivo_remoto}")
        sftp.close()
        print("[LOG] Arquivo enviado com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar arquivo via SFTP: {e}")
        ssh.close()
        raise
    try:
        # Configurar variável de ambiente para Matplotlib e executar Mininet
        comando = f"""
        export MPLCONFIGDIR=/tmp/matplotlib-config
        mkdir -p /tmp/matplotlib-config
        cd {REMOTE_PATH}
        
        # Tentar diferentes métodos de execução
        echo "=== Tentando executar Mininet v4.0 SUPER COMPLETA ==="
        
        # Método 1: Tentar sudo com versão 4.0 (SUPER COMPLETA)
        echo "Método 1: sudo com versão 4.0 SUPER COMPLETA"
        sudo python3 executa_cenario_mesh_v4.py {nome_arquivo_remoto} 2>&1 || {{
            echo "Sudo falhou, tentando método 2..."
            
            # Método 2: Tentar pkexec com versão 4.0
            echo "Método 2: pkexec com versão 4.0 SUPER COMPLETA"
            pkexec python3 executa_cenario_mesh_v4.py {nome_arquivo_remoto} 2>&1 || {{
                echo "Pkexec falhou, tentando método 3..."
                
                # Método 3: Tentar executar como usuário normal (vai falhar mas mostrar erro claro)
                echo "Método 3: usuário normal com versão 4.0"
                python3 executa_cenario_mesh_v4.py {nome_arquivo_remoto} 2>&1
            }}
        }}
        """
        print(f"[LOG] Executando Mininet com múltiplos métodos...")
        stdin, stdout, stderr = ssh.exec_command(comando)
        saida = stdout.read().decode() + stderr.read().decode()
        print("[LOG] Execução remota finalizada.")
        
        # Baixar logs após execução
        print("[LOG] Baixando logs da execução...")
        try:
            sftp = ssh.open_sftp()
            # Criar pasta results localmente
            os.makedirs('results', exist_ok=True)
            
            # Listar arquivos de log na VM
            stdin, stdout, stderr = ssh.exec_command(f"cd {REMOTE_PATH} && ls -1 *.csv *.log 2>/dev/null || echo 'Nenhum arquivo de log'")
            arquivos_log = stdout.read().decode().strip().split('\n')
            
            for arquivo in arquivos_log:
                if arquivo and arquivo != 'Nenhum arquivo de log':
                    arquivo = arquivo.strip()
                    print(f"[LOG] Baixando {arquivo}...")
                    try:
                        sftp.get(f"{REMOTE_PATH}/{arquivo}", f"results/{arquivo}")
                        print(f"[LOG] {arquivo} baixado com sucesso!")
                    except Exception as e:
                        print(f"[ERRO] Falha ao baixar {arquivo}: {e}")
            
            sftp.close()
        except Exception as e:
            print(f"[ERRO] Falha ao baixar logs: {e}")
            
    except Exception as e:
        print(f"[ERRO] Falha ao executar comando remoto: {e}")
        ssh.close()
        raise
    ssh.close()
    return saida

def gerar_script_robo(config, nome_cenario):
    """Gera script Python para executar no robô real"""
    
    script = f'''#!/usr/bin/env python3
"""
Script para robô real - Cenário: {nome_cenario}
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
ROBO_CONFIG = {{
    "serial_port": "/dev/ttyUSB0",  # Porta serial do robô
    "baudrate": 9600,
    "wifi_interface": "wlan0",
    "movement_speed": {config.get('propagation', {}).get('mobility_speed', 2.0)},
    "sampling_interval": {config.get('propagation', {}).get('sampling_interval', 1.0)}
}}

# Configurações do cenário
CENARIO_CONFIG = {json.dumps(config, indent=2)}

def conectar_robo():
    """Conecta com o robô via serial"""
    try:
        ser = serial.Serial(ROBO_CONFIG["serial_port"], ROBO_CONFIG["baudrate"], timeout=1)
        print(f"✅ Conectado ao robô em {{ROBO_CONFIG['serial_port']}}")
        return ser
    except Exception as e:
        print(f"❌ Erro ao conectar com robô: {{e}}")
        return None

def enviar_comando_robo(ser, comando):
    """Envia comando para o robô"""
    try:
        ser.write(f"{{comando}}\\n".encode())
        time.sleep(0.1)
        resposta = ser.readline().decode().strip()
        return resposta
    except Exception as e:
        print(f"❌ Erro ao enviar comando: {{e}}")
        return None

def obter_dados_wifi():
    """Obtém dados WiFi reais"""
    try:
        # RSSI
        cmd_rssi = f"iw dev {{ROBO_CONFIG['wifi_interface']}} link"
        result_rssi = subprocess.run(cmd_rssi, shell=True, capture_output=True, text=True)
        
        # Latência
        cmd_ping = "ping -c 1 -W 2 8.8.8.8"
        result_ping = subprocess.run(cmd_ping, shell=True, capture_output=True, text=True)
        
        # SSID atual
        cmd_ssid = f"iw dev {{ROBO_CONFIG['wifi_interface']}} link | grep SSID"
        result_ssid = subprocess.run(cmd_ssid, shell=True, capture_output=True, text=True)
        
        rssi = -100
        latency = 9999
        ssid = "N/A"
        
        # Parse RSSI
        for line in result_rssi.stdout.split('\\n'):
            if 'signal:' in line:
                try:
                    rssi = int(line.split('signal:')[1].split()[0])
                except:
                    pass
        
        # Parse latência
        for line in result_ping.stdout.split('\\n'):
            if 'time=' in line:
                try:
                    latency = float(line.split('time=')[1].split()[0])
                except:
                    pass
        
        # Parse SSID
        if result_ssid.stdout.strip():
            ssid = result_ssid.stdout.strip().split('SSID:')[1].strip()
        
        return {{
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'rssi': rssi,
            'latency': latency,
            'ssid': ssid,
            'position': [0, 0]  # Será atualizado pelo robô
        }}
        
    except Exception as e:
        print(f"❌ Erro ao obter dados WiFi: {{e}}")
        return None

def mover_robo(ser, x, y):
    """Move o robô para posição (x, y)"""
    comando = f"MOVE {{x}} {{y}}"
    resposta = enviar_comando_robo(ser, comando)
    print(f"🤖 Movendo para ({{x}}, {{y}}): {{resposta}}")
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
        log_file = f'robo_log_{{datetime.now().strftime("%Y%m%d_%H%M%S")}}.csv'
        
        with open(log_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'x', 'y', 'rssi', 'latency', 'ssid', 'handover']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Posição inicial
            pos_atual = [0, 0]
            ssid_anterior = None
            
            # Executar para cada station
            for station in CENARIO_CONFIG.get('stations', []):
                print(f"📱 Executando station: {{station['name']}}")
                
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
                    print(f"📊 Dados iniciais: {{dados}}")
                
                # Mover pela trajetória
                for i, ponto in enumerate(station['trajectory']):
                    x_dest, y_dest = ponto
                    
                    print(f"🚗 Movendo para ({{x_dest}}, {{y_dest}})")
                    
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
                            print(f"🔄 Handover detectado: {{ssid_anterior}} → {{dados['ssid']}}")
                        else:
                            dados['handover'] = False
                        
                        writer.writerow(dados)
                        print(f"📊 Dados: {{dados}}")
                        
                        ssid_anterior = dados['ssid']
        
        print(f"✅ Execução concluída! Log salvo em: {{log_file}}")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {{e}}")
    
    finally:
        ser.close()

if __name__ == "__main__":
    executar_cenario_robo()
'''
    
    return script

def baixar_log_robo(session_id, nome_cenario):
    """Baixa o log do robô para a máquina local"""
    try:
        # Criar diretório de logs se não existir
        logs_dir = "logs/robo_logs"
        os.makedirs(logs_dir, exist_ok=True)
        
        # Nome do arquivo local
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        local_log_file = f"{logs_dir}/robo_output_{session_id}_{nome_cenario}_{timestamp}.log"
        
        # Baixar via SCP
        remote_log_file = f"robo_output_{session_id}.log"
        scp_command = f"scp eduardowanderley@192.168.68.107:/home/eduardowanderley/{remote_log_file} {local_log_file}"
        
        print(f"📥 Baixando log do robô: {remote_log_file} -> {local_log_file}")
        result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Log baixado com sucesso: {local_log_file}")
            return local_log_file
        else:
            print(f"❌ Erro ao baixar log: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Exceção ao baixar log: {e}")
        return None

def enviar_para_robo(script_path, config):
    """Envia script para o robô usando conexão persistente"""
    
    saida = []
    session_id = str(uuid.uuid4())[:8]
    nome_cenario = os.path.basename(script_path).replace('.py', '')
    
    # Log do início da execução
    robo_logger.log_execucao_robo(
        os.path.basename(script_path), 
        "iniciando", 
        f"Sessão {session_id} - Enviando script para robô"
    )
    
    saida.append(f"🆔 Sessão: {session_id}")
    saida.append("🚀 Iniciando execução no robô...")
    saida.append(f"📋 Cenário: {os.path.basename(script_path)}")
    saida.append(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    
    # Método 1: Tentar via USB/Serial (fallback)
    saida.append("\n=== Tentando conectar via USB/Serial ===")
    try:
        import serial
        import glob
        portas = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        if portas:
            saida.append(f"📡 Portas encontradas: {portas}")
            porta = portas[0]
            saida.append(f"🔌 Tentando conectar em {porta}...")
            ser = serial.Serial(porta, 9600, timeout=1)
            ser.write(b"TEST\n")
            resposta = ser.readline().decode().strip()
            ser.close()
            if resposta:
                saida.append(f"✅ Robô USB respondeu: {resposta}")
                robo_logger.log_execucao_robo(
                    os.path.basename(script_path), 
                    "usb_conectado", 
                    f"Robô USB detectado em {porta}"
                )
                return "\n".join(saida)
            else:
                saida.append("⚠️ Robô USB não respondeu")
        else:
            saida.append("❌ Nenhuma porta USB encontrada")
    except Exception as e:
        saida.append(f"❌ Erro USB/Serial: {e}")
    
    # Método 2: Usar conexão persistente SSH
    saida.append("\n=== Usando conexão persistente SSH ===")
    
    try:
        # Verificar status da conexão
        if raspberry_conn.is_connected():
            saida.append("🔍 Status da conexão: ✅ Conectado")
        else:
            saida.append("🔍 Status da conexão: ❌ Não conectado")
            saida.append("🔗 Tentando estabelecer conexão...")
            if not raspberry_conn.connect():
                saida.append("❌ Falha ao estabelecer conexão SSH")
                return "\n".join(saida)
        
        # Verificar conexão SSH
        saida.append("🔗 Verificando conexão SSH...")
        test_result = raspberry_conn.execute_command("echo 'SSH OK'")
        if test_result['success']:
            saida.append("✅ Conexão SSH estabelecida!")
        else:
            saida.append("❌ Falha na conexão SSH")
            return "\n".join(saida)
        
        # Verificar espaço em disco
        saida.append("💾 Verificando espaço em disco...")
        df_result = raspberry_conn.execute_command("df -h /")
        if df_result['success']:
            saida.append(f"📊 Espaço disponível: {df_result['output'].strip()}")
        else:
            saida.append("⚠️ Não foi possível verificar espaço em disco")
        
        # Enviar script
        remote_path = f'/home/eduardowanderley/{os.path.basename(script_path)}'
        saida.append(f"📤 Enviando script para: {remote_path}")
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(script_path)
        saida.append(f"📁 Tamanho do arquivo: {file_size} bytes")
        
        saida.append("🔄 Iniciando upload...")
        start_upload = datetime.now()
        
        upload_success = raspberry_conn.upload_file(script_path, remote_path)
        upload_time = (datetime.now() - start_upload).total_seconds()
        
        if upload_success:
            saida.append(f"✅ Script enviado com sucesso! (Tempo: {upload_time:.2f}s)")
            
            # Log do upload
            robo_logger.log_conexao_ssh(
                '192.168.68.107', 
                'upload_sucesso', 
                f'Arquivo enviado: {os.path.basename(script_path)} -> {remote_path}'
            )
            
            # Verificar se arquivo foi criado
            saida.append("🔍 Verificando arquivo no Raspberry Pi...")
            try:
                check_result = raspberry_conn.execute_command(f"ls -la {remote_path}")
                if check_result['success']:
                    saida.append(f"📄 Arquivo criado: {check_result['output'].strip()}")
                else:
                    saida.append(f"⚠️ Erro ao verificar arquivo: {check_result['error']}")
            except Exception as e:
                saida.append(f"❌ Exceção ao verificar arquivo: {e}")
            
            # Executar no robô
            comando_execucao = f'python3 {remote_path}'
            saida.append(f"🚀 Executando: {comando_execucao}")
            saida.append("⏳ Iniciando execução em background...")
            try:
                saida.append("🔄 Preparando comando nohup...")
                comando_nohup = f'nohup {comando_execucao} > robo_output_{session_id}.log 2>&1 & echo $!'
                saida.append(f"📝 Comando completo: {comando_nohup}")
                start_exec = datetime.now()
                saida.append("⚡ Executando comando...")
                result = raspberry_conn.execute_command(comando_nohup)
                exec_time = (datetime.now() - start_exec).total_seconds()
                saida.append(f"⏱️ Comando executado em {exec_time:.2f}s")
            except Exception as e:
                saida.append(f"❌ Erro ao executar comando: {e}")
                return "\n".join(saida)
            
            if result['success']:
                saida.append("✅ Comando executado com sucesso!")
                saida.append(f"📄 Saída do comando: '{result['output'].strip()}'")
                pid = result['output'].strip()
                if pid.isdigit():
                    saida.append(f"✅ Script iniciado no Raspberry Pi!")
                    saida.append(f"🆔 PID do processo: {pid}")
                    saida.append(f"⏱️ Tempo de execução: {exec_time:.2f}s")
                    saida.append(f"📊 Log file: robo_output_{session_id}.log")
                    saida.append("🔄 Monitorando execução em background...")
                    saida.append("🔍 Verificando se processo está ativo...")
                    try:
                        ps_result = raspberry_conn.execute_command(f"ps -p {pid}")
                        if ps_result['success'] and pid in ps_result['output']:
                            saida.append("✅ Processo confirmado ativo!")
                        else:
                            saida.append("⚠️ Processo não encontrado - pode ter terminado rapidamente")
                    except Exception as e:
                        saida.append(f"❌ Erro ao verificar processo: {e}")
                    
                    # Baixar log para máquina local
                    saida.append("\n=== Baixando log para máquina local ===")
                    local_log_path = baixar_log_robo(session_id, nome_cenario)
                    if local_log_path:
                        saida.append(f"📥 Log salvo localmente: {local_log_path}")
                        saida.append("💡 Você pode acessar o log em tempo real com:")
                        saida.append(f"   tail -f {local_log_path}")
                    else:
                        saida.append("⚠️ Não foi possível baixar o log automaticamente")
                        saida.append("💡 Baixe manualmente com:")
                        saida.append(f"   scp eduardowanderley@192.168.68.107:/home/eduardowanderley/robo_output_{session_id}.log .")
                else:
                    saida.append(f"⚠️ PID inválido retornado: '{pid}'")
                    saida.append("🔍 Verificando se processo foi iniciado...")
                    try:
                        ps_result = raspberry_conn.execute_command("ps aux | grep python3 | grep -v grep")
                        if ps_result['success']:
                            saida.append(f"📊 Processos Python ativos: {ps_result['output'].strip()}")
                    except Exception as e:
                        saida.append(f"❌ Erro ao verificar processos: {e}")
                
                robo_logger.log_execucao_robo(
                    os.path.basename(script_path), 
                    "executando", 
                    f"Script iniciado - PID: {pid}, Log: robo_output_{session_id}.log, Tempo: {exec_time:.2f}s"
                )
                return "\n".join(saida)
            else:
                saida.append(f"❌ Erro ao executar: {result['error']}")
                saida.append(f"⏱️ Tempo até erro: {exec_time:.2f}s")
                robo_logger.log_execucao_robo(
                    os.path.basename(script_path), 
                    "erro_execucao", 
                    f"Erro: {result['error']}, Tempo: {exec_time:.2f}s"
                )
                return "\n".join(saida)
        else:
            saida.append("❌ Não foi possível estabelecer conexão SSH")
            robo_logger.log_execucao_robo(
                os.path.basename(script_path), 
                "falha_conexao", 
                "Falha na conexão SSH"
            )
            return "\n".join(saida)
    except Exception as e:
        saida.append(f"❌ Erro SSH: {e}")
        robo_logger.log_execucao_robo(
            os.path.basename(script_path), 
            "erro_ssh", 
            f"Erro SSH: {str(e)}"
        )
        return "\n".join(saida)
    
    # Método 3: Salvar script localmente para transferência manual
    saida.append("\n=== Salvando script para transferência manual ===")
    saida.append(f"📁 Script salvo em: {os.path.abspath(script_path)}")
    saida.append("💡 Copie o script para o robô manualmente e execute:")
    saida.append(f"   python3 {os.path.basename(script_path)}")
    robo_logger.log_execucao_robo(
        os.path.basename(script_path), 
        "manual_required", 
        "Execução manual necessária"
    )
    return "\n".join(saida)

@app.route('/executar/<nome>')
def executar(nome):
    caminho = os.path.join(CENARIOS_DIR, nome)
    if not os.path.exists(caminho):
        flash('Cenário não encontrado!', 'danger')
        return redirect(url_for('index'))
    try:
        saida = executar_remoto(caminho, nome)
        sucesso = "Traceback" not in saida
    except Exception as e:
        saida = str(e)
        sucesso = False
    return render_template('execucao.html', nome=nome, saida=saida, sucesso=sucesso)

@app.route('/executar_robo/<nome>')
def executar_robo(nome):
    """Executa cenário no robô real conectado via USB/Serial"""
    caminho = os.path.join(CENARIOS_DIR, nome)
    if not os.path.exists(caminho):
        flash('Cenário não encontrado!', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Carregar configuração do cenário
        with open(caminho, 'r') as f:
            config = json.load(f)
        
        # Gerar script para o robô
        script_robo = gerar_script_robo(config, nome)
        
        # Salvar script temporário
        script_path = f'robo_script_{nome.replace(".json", "")}.py'
        with open(script_path, 'w') as f:
            f.write(script_robo)
        
        # Tentar enviar para o robô via USB/Serial
        saida = enviar_para_robo(script_path, config)
        print("\n===== LOG DETALHADO DA EXECUÇÃO =====\n")
        print(saida)
        print("\n===== FIM DO LOG =====\n")
        sucesso = "ERRO" not in saida.upper()
        
        flash(f'Script enviado para o robô! {saida}', 'success' if sucesso else 'warning')
        
    except Exception as e:
        saida = f"Erro ao conectar com robô: {e}"
        sucesso = False
        flash(saida, 'danger')
    
    return render_template('execucao_robo.html', nome=nome, saida=saida, sucesso=sucesso, config=config)

@app.route('/status_raspberry')
def status_raspberry():
    """Retorna status da conexão com o Raspberry Pi"""
    status = raspberry_conn.get_status()
    wifi_info = None
    
    if status['connected']:
        try:
            wifi_info = raspberry_conn.get_wifi_info()
        except:
            wifi_info = "Erro ao obter informações WiFi"
    
    return {
        'connection': status,
        'wifi_info': wifi_info,
        'logs_recentes': robo_logger.get_logs_recentes(limit=10)
    }

@app.route('/logs_sistema')
def logs_sistema():
    """Retorna logs do sistema"""
    tipo = request.args.get('tipo', 'all')
    limit = int(request.args.get('limit', 50))
    
    logs = robo_logger.get_logs_recentes(tipo=tipo, limit=limit)
    return {'logs': logs}

@app.route('/logs_robo')
def logs_robo():
    """Página para visualizar logs do robô baixados"""
    logs_dir = "logs/robo_logs"
    logs = []
    
    if os.path.exists(logs_dir):
        for arquivo in os.listdir(logs_dir):
            if arquivo.endswith('.log'):
                caminho = os.path.join(logs_dir, arquivo)
                stat = os.stat(caminho)
                logs.append({
                    'nome': arquivo,
                    'caminho': caminho,
                    'tamanho': stat.st_size,
                    'data_modificacao': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    # Ordenar por data de modificação (mais recente primeiro)
    logs.sort(key=lambda x: x['data_modificacao'], reverse=True)
    
    return render_template('logs_robo.html', logs=logs)

@app.route('/visualizar_log/<nome_arquivo>')
def visualizar_log(nome_arquivo):
    """Visualiza o conteúdo de um log específico"""
    logs_dir = "logs/robo_logs"
    caminho = os.path.join(logs_dir, nome_arquivo)
    
    if not os.path.exists(caminho):
        flash('Arquivo de log não encontrado!', 'danger')
        return redirect(url_for('logs_robo'))
    
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Estatísticas do log
        linhas = conteudo.split('\n')
        tamanho = os.path.getsize(caminho)
        stat = os.stat(caminho)
        data_modificacao = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template('visualizar_log.html', 
                             nome_arquivo=nome_arquivo,
                             conteudo=conteudo,
                             linhas=len(linhas),
                             tamanho=tamanho,
                             data_modificacao=data_modificacao)
    except Exception as e:
        flash(f'Erro ao ler arquivo: {e}', 'danger')
        return redirect(url_for('logs_robo'))

@app.route('/baixar_log_antigo/<session_id>')
def baixar_log_antigo(session_id):
    """Baixa um log antigo do Raspberry Pi"""
    try:
        nome_cenario = request.args.get('cenario', 'desconhecido')
        local_log_path = baixar_log_robo(session_id, nome_cenario)
        
        if local_log_path:
            flash(f'Log baixado com sucesso: {local_log_path}', 'success')
        else:
            flash('Erro ao baixar log do Raspberry Pi', 'warning')
            
    except Exception as e:
        flash(f'Erro: {e}', 'danger')
    
    return redirect(url_for('logs_robo'))

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print("📡 Interface web disponível em: http://localhost:5000")
    print("🤖 Configurado para conectar no Raspberry Pi: 192.168.68.107")
    
    # Iniciar conexão persistente com Raspberry Pi
    print("🔗 Iniciando conexão persistente com Raspberry Pi...")
    if raspberry_conn.connect():
        print("✅ Conexão persistente estabelecida!")
    else:
        print("⚠️ Conexão persistente não estabelecida - será tentada automaticamente")
    
    app.run(host='0.0.0.0', port=5000, debug=False)  # Desabilitar debug para evitar reinicializações 