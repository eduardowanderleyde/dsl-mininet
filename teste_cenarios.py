#!/usr/bin/env python3

import json
import os
import sys

def validar_cenario(config):
    """Valida se um cenário está configurado corretamente"""
    erros = []
    
    # Verificar campos obrigatórios
    if 'ssid' not in config:
        erros.append("Campo 'ssid' é obrigatório")
    
    if 'channel' not in config:
        erros.append("Campo 'channel' é obrigatório")
    elif not isinstance(config['channel'], int) or config['channel'] < 1 or config['channel'] > 14:
        erros.append("Canal deve ser um número entre 1 e 14")
    
    if 'wait' not in config:
        erros.append("Campo 'wait' é obrigatório")
    elif not isinstance(config['wait'], int) or config['wait'] < 1:
        erros.append("Tempo de espera deve ser um número positivo")
    
    # Verificar APs
    if 'aps' not in config:
        erros.append("Campo 'aps' é obrigatório")
    elif not isinstance(config['aps'], list):
        erros.append("APs deve ser uma lista")
    else:
        for i, ap in enumerate(config['aps']):
            if 'name' not in ap:
                erros.append(f"AP {i+1}: campo 'name' é obrigatório")
            if 'x' not in ap or 'y' not in ap:
                erros.append(f"AP {i+1}: campos 'x' e 'y' são obrigatórios")
            elif not isinstance(ap['x'], (int, float)) or not isinstance(ap['y'], (int, float)):
                erros.append(f"AP {i+1}: coordenadas devem ser números")
    
    # Verificar stations
    if 'stations' not in config:
        erros.append("Campo 'stations' é obrigatório")
    elif not isinstance(config['stations'], list):
        erros.append("Stations deve ser uma lista")
    else:
        for i, sta in enumerate(config['stations']):
            if 'name' not in sta:
                erros.append(f"Station {i+1}: campo 'name' é obrigatório")
            if 'start_x' not in sta or 'start_y' not in sta:
                erros.append(f"Station {i+1}: campos 'start_x' e 'start_y' são obrigatórios")
            elif not isinstance(sta['start_x'], (int, float)) or not isinstance(sta['start_y'], (int, float)):
                erros.append(f"Station {i+1}: coordenadas iniciais devem ser números")
            
            if 'trajectory' not in sta:
                erros.append(f"Station {i+1}: campo 'trajectory' é obrigatório")
            elif not isinstance(sta['trajectory'], list):
                erros.append(f"Station {i+1}: trajetória deve ser uma lista")
            else:
                for j, point in enumerate(sta['trajectory']):
                    if not isinstance(point, list) or len(point) != 2:
                        erros.append(f"Station {i+1}, ponto {j+1}: deve ser uma lista com 2 coordenadas [x,y]")
                    elif not isinstance(point[0], (int, float)) or not isinstance(point[1], (int, float)):
                        erros.append(f"Station {i+1}, ponto {j+1}: coordenadas devem ser números")
    
    return erros

def mostrar_preview(config):
    """Mostra um preview do cenário"""
    print(f"\n📡 CENÁRIO: {config.get('ssid', 'N/A')}")
    print(f"📶 Canal: {config.get('channel', 'N/A')}")
    print(f"⏱️  Tempo de espera: {config.get('wait', 'N/A')}s")
    
    print(f"\n🏢 APs ({len(config.get('aps', []))}):")
    for ap in config.get('aps', []):
        print(f"  • {ap['name']} em ({ap['x']}, {ap['y']})")
    
    print(f"\n📱 Stations ({len(config.get('stations', []))}):")
    for sta in config.get('stations', []):
        print(f"  • {sta['name']}: início em ({sta['start_x']}, {sta['start_y']})")
        print(f"    Trajetória: {len(sta['trajectory'])} pontos")
        for i, point in enumerate(sta['trajectory']):
            print(f"      {i+1}. ({point[0]}, {point[1]})")

def testar_cenarios():
    """Testa todos os cenários de exemplo"""
    cenarios_dir = "cenarios"
    
    if not os.path.exists(cenarios_dir):
        print(f"❌ Diretório {cenarios_dir} não encontrado")
        return
    
    arquivos_json = [f for f in os.listdir(cenarios_dir) if f.endswith('.json')]
    
    if not arquivos_json:
        print(f"❌ Nenhum arquivo JSON encontrado em {cenarios_dir}")
        return
    
    print(f"🔍 Testando {len(arquivos_json)} cenários...\n")
    
    for arquivo in sorted(arquivos_json):
        caminho = os.path.join(cenarios_dir, arquivo)
        print(f"📄 {arquivo}:")
        
        try:
            with open(caminho, 'r') as f:
                config = json.load(f)
            
            erros = validar_cenario(config)
            
            if erros:
                print("  ❌ ERROS:")
                for erro in erros:
                    print(f"    • {erro}")
            else:
                print("  ✅ Válido")
                mostrar_preview(config)
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Erro de JSON: {e}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        
        print("-" * 50)

def criar_cenario_teste():
    """Cria um cenário de teste simples"""
    config = {
        "ssid": "teste",
        "channel": 1,
        "wait": 2,
        "aps": [
            {"name": "ap1", "x": 10.0, "y": 20.0},
            {"name": "ap2", "x": 30.0, "y": 20.0}
        ],
        "stations": [
            {
                "name": "sta1",
                "start_x": 5.0,
                "start_y": 20.0,
                "trajectory": [[15.0, 20.0], [25.0, 20.0], [35.0, 20.0]]
            }
        ]
    }
    
    os.makedirs("cenarios", exist_ok=True)
    with open("cenarios/cenario_teste.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Cenário de teste criado: cenarios/cenario_teste.json")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "criar":
            criar_cenario_teste()
        else:
            print("Uso: python3 teste_cenarios.py [criar]")
    else:
        testar_cenarios() 