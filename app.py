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
        print(f"[LOG] Executando comando remoto: cd {REMOTE_PATH} && python3 executa_cenario.py {nome_arquivo_remoto}")
        stdin, stdout, stderr = ssh.exec_command(
            f"cd {REMOTE_PATH} && python3 executa_cenario.py {nome_arquivo_remoto}"
        )
        saida = stdout.read().decode() + stderr.read().decode()
        print("[LOG] Execução remota finalizada.")
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