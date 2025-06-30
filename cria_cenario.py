import json
import sys

def print_preview(config):
    print("\n--- PREVIEW DO CENÁRIO ---")
    print(f"SSID: {config.get('ssid', 'meshNet')}")
    print(f"Canal: {config.get('channel', 1)}")
    print(f"Tempo de espera: {config.get('wait', 2)}s")
    print("APs:")
    for ap in config['aps']:
        print(f"  {ap['name']} - pos=({ap['x']}, {ap['y']})")
    print("Stations:")
    for sta in config['stations']:
        print(f"  {sta['name']} - início=({sta['start_x']}, {sta['start_y']}) trajetoria={sta['trajectory']}")
    print("-------------------------\n")

def input_float(msg, default=None):
    while True:
        val = input(msg + (f" [{default}]" if default is not None else "") + ": ")
        if val == '' and default is not None:
            return default
        try:
            return float(val)
        except ValueError:
            print("Valor inválido!")

def input_int(msg, default=None):
    while True:
        val = input(msg + (f" [{default}]" if default is not None else "") + ": ")
        if val == '' and default is not None:
            return default
        try:
            return int(val)
        except ValueError:
            print("Valor inválido!")

def criar_cenario_zero():
    config = {"aps": [], "stations": []}
    config["ssid"] = input("SSID da rede [meshNet]: ") or "meshNet"
    config["channel"] = input_int("Canal WiFi", 1)
    n_aps = input_int("Quantos APs (1-4)?", 2)
    for i in range(1, n_aps+1):
        x = input_float(f"AP{i} posição X", i*10)
        y = input_float(f"AP{i} posição Y", 20)
        config["aps"].append({"name": f"ap{i}", "x": x, "y": y})
    n_stas = input_int("Quantas stations (1-3)?", 1)
    for i in range(1, n_stas+1):
        x = input_float(f"Station{i} posição inicial X", 5)
        y = input_float(f"Station{i} posição inicial Y", 5)
        print("\nTipo de movimento:")
        print("1 - Linha reta")
        print("2 - Triângulo")
        print("3 - Personalizado")
        tipo = input_int("Tipo", 1)
        trajectory = []
        if tipo == 1:
            num_pontos = input_int("Quantos pontos na linha reta?", 2)
            for p in range(num_pontos):
                px = input_float(f"  Ponto {p+1} X", x + (p+1)*5)
                py = input_float(f"  Ponto {p+1} Y", y)
                trajectory.append([px, py])
        elif tipo == 2:
            for t in ["A", "B", "C"]:
                px = input_float(f"  Ponto {t} X", x + (ord(t)-65)*5)
                py = input_float(f"  Ponto {t} Y", y + (ord(t)-65)*5)
                trajectory.append([px, py])
        elif tipo == 3:
            num_pontos = input_int("Quantos pontos?", 2)
            for p in range(num_pontos):
                px = input_float(f"  Ponto {p+1} X", x + (p+1)*3)
                py = input_float(f"  Ponto {p+1} Y", y)
                trajectory.append([px, py])
        config["stations"].append({
            "name": f"sta{i}",
            "start_x": x,
            "start_y": y,
            "trajectory": trajectory
        })
    config["wait"] = input_int("Tempo de espera em cada ponto (s)", 2)
    return config

def cenario_linha_reta():
    return {
        "ssid": "meshNet",
        "channel": 1,
        "aps": [
            {"name": "ap1", "x": 10, "y": 20},
            {"name": "ap2", "x": 30, "y": 20}
        ],
        "stations": [
            {
                "name": "sta1",
                "start_x": 5,
                "start_y": 20,
                "trajectory": [[15, 20], [25, 20], [35, 20]]
            }
        ],
        "wait": 2
    }

def cenario_triangulo():
    return {
        "ssid": "meshNet",
        "channel": 1,
        "aps": [
            {"name": "ap1", "x": 10, "y": 10},
            {"name": "ap2", "x": 30, "y": 10},
            {"name": "ap3", "x": 20, "y": 30}
        ],
        "stations": [
            {
                "name": "sta1",
                "start_x": 15,
                "start_y": 15,
                "trajectory": [[25, 15], [20, 25], [15, 15]]
            }
        ],
        "wait": 2
    }

def cenario_quadrado_mesh():
    return {
        "ssid": "meshNet",
        "channel": 1,
        "aps": [
            {"name": "ap1", "x": 10, "y": 10},
            {"name": "ap2", "x": 30, "y": 10},
            {"name": "ap3", "x": 30, "y": 30},
            {"name": "ap4", "x": 10, "y": 30}
        ],
        "stations": [
            {
                "name": "sta1",
                "start_x": 5,
                "start_y": 5,
                "trajectory": [[35, 5], [35, 35], [5, 35], [5, 5]]
            },
            {
                "name": "sta2",
                "start_x": 20,
                "start_y": 20,
                "trajectory": [[25, 25], [15, 25], [15, 15], [25, 15], [25, 25]]
            }
        ],
        "wait": 2
    }

def escolher_cenario_pronto():
    cenarios = [
        ("Linha Reta (handover simples)", cenario_linha_reta),
        ("Triângulo de APs", cenario_triangulo),
        ("Quadrado Mesh", cenario_quadrado_mesh)
    ]
    while True:
        print("\nCenários prontos:")
        for i, (nome, _) in enumerate(cenarios, 1):
            print(f"[{i}] {nome}")
        print(f"[{len(cenarios)+1}] Voltar")
        op = input_int("Escolha", 1)
        if 1 <= op <= len(cenarios):
            config = cenarios[op-1][1]()
            print_preview(config)
            edit = input("Editar esse cenário? (s/n) [n]: ") or 'n'
            if edit.lower() == 's':
                config = editar_cenario(config)
            return config
        elif op == len(cenarios)+1:
            return None
        else:
            print("Opção inválida!")

def editar_cenario(config):
    print("\nEdição rápida: (pressione Enter para manter o valor atual)")
    config["ssid"] = input(f"SSID [{config['ssid']}]: ") or config["ssid"]
    config["channel"] = input_int("Canal WiFi", config["channel"])
    config["wait"] = input_int("Tempo de espera em cada ponto (s)", config["wait"])
    # Não edita APs/stations por simplicidade, mas pode ser expandido
    return config

def salvar_config(config):
    nome = input("Nome do arquivo para salvar [cenario.json]: ") or "cenario.json"
    with open(nome, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Cenário salvo em {nome}!")

def main():
    while True:
        print("\n==== MENU PRINCIPAL ====")
        print("[1] Criar cenário do zero")
        print("[2] Escolher cenário pronto")
        print("[3] Sair")
        op = input_int("Escolha", 1)
        if op == 1:
            config = criar_cenario_zero()
            print_preview(config)
            if input("Salvar esse cenário? (s/n) [s]: ") or 's' == 's':
                salvar_config(config)
        elif op == 2:
            config = escolher_cenario_pronto()
            if config:
                print_preview(config)
                if input("Salvar esse cenário? (s/n) [s]: ") or 's' == 's':
                    salvar_config(config)
        elif op == 3:
            print("Saindo...")
            sys.exit(0)
        else:
            print("Opção inválida!")

if __name__ == '__main__':
    main() 