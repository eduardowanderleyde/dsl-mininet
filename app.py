import os
import json
import subprocess
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import paramiko

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
        # APs
        ap_names = request.form.getlist('ap_name')
        ap_xs = request.form.getlist('ap_x')
        ap_ys = request.form.getlist('ap_y')
        aps = []
        for n, x, y in zip(ap_names, ap_xs, ap_ys):
            if n.strip() != '':
                aps.append({"name": n.strip(), "x": float(x), "y": float(y)})
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
            "stations": stations
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
        echo "=== Tentando executar Mininet ==="
        
        # Método 1: Tentar sudo (pode falhar se precisar de senha)
        echo "Método 1: sudo"
        sudo python3 executa_cenario.py {nome_arquivo_remoto} 2>&1 || {{
            echo "Sudo falhou, tentando método 2..."
            
            # Método 2: Tentar pkexec
            echo "Método 2: pkexec"
            pkexec python3 executa_cenario.py {nome_arquivo_remoto} 2>&1 || {{
                echo "Pkexec falhou, tentando método 3..."
                
                # Método 3: Tentar executar como usuário normal (vai falhar mas mostrar erro claro)
                echo "Método 3: usuário normal"
                python3 executa_cenario.py {nome_arquivo_remoto} 2>&1
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 