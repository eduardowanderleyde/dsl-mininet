#!/usr/bin/env python3
"""
Script para testes manuais incrementais de conectividade
Permite ajustar parâmetros e testar diferentes configurações
"""

import json
import time
import subprocess
import os
from datetime import datetime

def criar_cenario_manual(ap1_x, ap2_x, ap_y=20.0, start_x=0.0, end_x=40.0, steps=10):
    """Cria um cenário com parâmetros manuais"""
    
    # Calcular pontos intermediários
    step_size = (end_x - start_x) / (steps - 1)
    trajectory = []
    
    for i in range(steps):
        x = start_x + (i * step_size)
        trajectory.append([x, ap_y])
    
    cenario = {
        "ssid": "meshNet",
        "channel": 1,
        "wait": 2,
        "aps": [
            {
                "name": "ap1",
                "x": ap1_x,
                "y": ap_y
            },
            {
                "name": "ap2", 
                "x": ap2_x,
                "y": ap_y
            }
        ],
        "stations": [
            {
                "name": "sta1",
                "start_x": start_x,
                "start_y": ap_y,
                "trajectory": trajectory
            }
        ]
    }
    
    return cenario

def executar_teste_manual(cenario, nome_teste):
    """Executa um teste manual"""
    
    # Salvar cenário
    with open(f"cenarios/manual_{nome_teste}.json", "w") as f:
        json.dump(cenario, f, indent=2)
    
    print(f"\n🧪 Executando teste manual: {nome_teste}")
    print(f"   AP1: ({cenario['aps'][0]['x']}, {cenario['aps'][0]['y']})")
    print(f"   AP2: ({cenario['aps'][1]['x']}, {cenario['aps'][1]['y']})")
    print(f"   Movimento: ({cenario['stations'][0]['start_x']}, {cenario['stations'][0]['start_y']}) → ({cenario['stations'][0]['trajectory'][-1][0]}, {cenario['stations'][0]['trajectory'][-1][1]})")
    
    # Executar
    try:
        cmd = f"sudo python3 executa_cenario_mesh_v2.py cenarios/manual_{nome_teste}.json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("   ✅ Teste executado com sucesso")
            return True
        else:
            print(f"   ❌ Erro: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def analisar_resultado_manual(nome_teste):
    """Analisa resultado de um teste manual"""
    
    log_file = "results/sta1_mesh_v2_log.csv"
    
    if not os.path.exists(log_file):
        print(f"   ❌ Log não encontrado")
        return None
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            print(f"   ❌ Log vazio")
            return None
        
        # Parse CSV
        data = []
        for line in lines[1:]:
            values = line.strip().split(',')
            if len(values) >= 5:
                data.append({
                    'position': values[1].strip('"'),
                    'rssi': int(values[2]),
                    'latency': float(values[3]),
                    'ap_conectado': values[4]
                })
        
        # Análise rápida
        aps_conectados = {}
        handovers = 0
        ap_anterior = None
        
        for entry in data:
            ap_atual = entry['ap_conectado']
            
            if ap_atual not in aps_conectados:
                aps_conectados[ap_atual] = 0
            aps_conectados[ap_atual] += 1
            
            if ap_anterior and ap_anterior != ap_atual:
                handovers += 1
            
            ap_anterior = ap_atual
        
        print(f"   📊 Resultado: {len(data)} registros, {handovers} handovers")
        print(f"   📡 APs: {aps_conectados}")
        
        # Mostrar detalhes das posições
        print(f"   📍 Posições:")
        for entry in data:
            print(f"      {entry['position']} → {entry['ap_conectado']} (RSSI: {entry['rssi']}, Lat: {entry['latency']:.3f}ms)")
        
        return {
            'nome_teste': nome_teste,
            'total_registros': len(data),
            'handovers': handovers,
            'aps_conectados': aps_conectados,
            'dados': data
        }
        
    except Exception as e:
        print(f"   ❌ Erro na análise: {e}")
        return None

def salvar_resultado(resultado, arquivo_log="resultados_manuais.md"):
    """Salva resultado no log de testes manuais"""
    
    if not resultado:
        return
    
    # Criar ou carregar log existente
    if os.path.exists(arquivo_log):
        with open(arquivo_log, 'r') as f:
            conteudo = f.read()
    else:
        conteudo = "# 📊 Log de Testes Manuais - DSL Mininet-WiFi\n\n"
    
    # Adicionar novo resultado
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    novo_resultado = f"""
## Teste: {resultado['nome_teste']} - {timestamp}

- **Registros:** {resultado['total_registros']}
- **Handovers:** {resultado['handovers']}
- **APs Conectados:** {resultado['aps_conectados']}

### Detalhes das Posições:
"""
    
    for entry in resultado['dados']:
        novo_resultado += f"- {entry['position']} → {entry['ap_conectado']} (RSSI: {entry['rssi']}, Lat: {entry['latency']:.3f}ms)\n"
    
    novo_resultado += "\n---\n"
    
    # Salvar
    with open(arquivo_log, 'w') as f:
        f.write(conteudo + novo_resultado)
    
    print(f"   💾 Resultado salvo em: {arquivo_log}")

def main():
    """Interface principal para testes manuais"""
    
    print("🔬 Testes Manuais Incrementais - DSL Mininet-WiFi")
    print("=" * 50)
    
    while True:
        print(f"\n📋 Opções:")
        print(f"1. Executar teste com parâmetros padrão")
        print(f"2. Executar teste com parâmetros customizados")
        print(f"3. Ver resultados anteriores")
        print(f"4. Sair")
        
        opcao = input(f"\nEscolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            # Teste padrão
            nome = input("Nome do teste: ").strip()
            if not nome:
                nome = f"teste_{int(time.time())}"
            
            cenario = criar_cenario_manual(
                ap1_x=10.0,
                ap2_x=20.0,
                start_x=5.0,
                end_x=25.0
            )
            
            sucesso = executar_teste_manual(cenario, nome)
            if sucesso:
                time.sleep(3)
                resultado = analisar_resultado_manual(nome)
                salvar_resultado(resultado)
        
        elif opcao == "2":
            # Teste customizado
            nome = input("Nome do teste: ").strip()
            if not nome:
                nome = f"teste_{int(time.time())}"
            
            print(f"\n📐 Configuração dos APs:")
            ap1_x = float(input("AP1 X (padrão: 10.0): ") or "10.0")
            ap2_x = float(input("AP2 X (padrão: 20.0): ") or "20.0")
            ap_y = float(input("AP Y (padrão: 20.0): ") or "20.0")
            
            print(f"\n📍 Configuração do movimento:")
            start_x = float(input("Início X (padrão: 5.0): ") or "5.0")
            end_x = float(input("Fim X (padrão: 25.0): ") or "25.0")
            steps = int(input("Passos (padrão: 10): ") or "10")
            
            cenario = criar_cenario_manual(
                ap1_x=ap1_x,
                ap2_x=ap2_x,
                ap_y=ap_y,
                start_x=start_x,
                end_x=end_x,
                steps=steps
            )
            
            sucesso = executar_teste_manual(cenario, nome)
            if sucesso:
                time.sleep(3)
                resultado = analisar_resultado_manual(nome)
                salvar_resultado(resultado)
        
        elif opcao == "3":
            # Ver resultados
            arquivo_log = "resultados_manuais.md"
            if os.path.exists(arquivo_log):
                with open(arquivo_log, 'r') as f:
                    print(f"\n📄 Últimos resultados:")
                    print(f.read())
            else:
                print(f"\n❌ Nenhum resultado encontrado")
        
        elif opcao == "4":
            print(f"\n👋 Saindo...")
            break
        
        else:
            print(f"\n❌ Opção inválida")

if __name__ == "__main__":
    main() 