#!/usr/bin/env python3
"""
Script para testar limites de conectividade e handover
Testa diferentes distâncias e documenta automaticamente os resultados
"""

import json
import time
import subprocess
import os
from datetime import datetime

def criar_cenario_teste(ap1_x, ap2_x, ap_y=20.0, start_x=0.0, end_x=40.0, steps=10):
    """Cria um cenário de teste com APs em posições específicas"""
    
    # Calcular pontos intermediários para movimento
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

def executar_teste(cenario, nome_teste):
    """Executa um teste específico e retorna os resultados"""
    
    # Salvar cenário temporário
    with open(f"cenarios/temp_{nome_teste}.json", "w") as f:
        json.dump(cenario, f, indent=2)
    
    print(f"\n🧪 Executando teste: {nome_teste}")
    print(f"   AP1: ({cenario['aps'][0]['x']}, {cenario['aps'][0]['y']})")
    print(f"   AP2: ({cenario['aps'][1]['x']}, {cenario['aps'][1]['y']})")
    print(f"   Movimento: ({cenario['stations'][0]['start_x']}, {cenario['stations'][0]['start_y']}) → ({cenario['stations'][0]['trajectory'][-1][0]}, {cenario['stations'][0]['trajectory'][-1][1]})")
    
    # Executar teste
    try:
        cmd = f"sudo python3 executa_cenario_mesh_v2.py cenarios/temp_{nome_teste}.json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("   ✅ Teste executado com sucesso")
            return True
        else:
            print(f"   ❌ Erro na execução: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ Timeout na execução")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def analisar_resultados(nome_teste):
    """Analisa os resultados de um teste específico"""
    
    log_file = f"results/sta1_mesh_v2_log.csv"
    
    if not os.path.exists(log_file):
        print(f"   ❌ Arquivo de log não encontrado: {log_file}")
        return None
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            print(f"   ❌ Log vazio ou incompleto")
            return None
        
        # Parse CSV com suporte a campos com vírgulas
        headers = lines[0].strip().split(',')
        data = []
        
        for line in lines[1:]:
            try:
                # Parse manual para lidar com vírgulas dentro de aspas
                parts = []
                current = ""
                in_quotes = False
                
                for char in line.strip():
                    if char == '"':
                        in_quotes = not in_quotes
                    elif char == ',' and not in_quotes:
                        parts.append(current.strip())
                        current = ""
                    else:
                        current += char
                
                parts.append(current.strip())
                
                if len(parts) >= 5:
                    # Limpar aspas extras
                    time_val = parts[0].strip('"')
                    position = parts[1].strip('"')
                    rssi_str = parts[2].strip('"')
                    latency_str = parts[3].strip('"')
                    ap_conectado = parts[4].strip('"')
                    
                    data.append({
                        'time': time_val,
                        'position': position,
                        'rssi': int(rssi_str),
                        'latency': float(latency_str),
                        'ap_conectado': ap_conectado
                    })
            except (ValueError, IndexError) as e:
                print(f"   ⚠️ Erro ao processar linha: {line.strip()} - {e}")
                continue
        
        # Análise
        aps_conectados = {}
        handovers = 0
        conectado_count = 0
        desconectado_count = 0
        
        ap_anterior = None
        for entry in data:
            ap_atual = entry['ap_conectado']
            
            # Contar APs
            if ap_atual not in aps_conectados:
                aps_conectados[ap_atual] = 0
            aps_conectados[ap_atual] += 1
            
            # Contar conectividade
            if ap_atual == 'desconectado':
                desconectado_count += 1
            else:
                conectado_count += 1
            
            # Detectar handovers
            if ap_anterior and ap_anterior != ap_atual:
                handovers += 1
            
            ap_anterior = ap_atual
        
        # Calcular métricas
        total_registros = len(data)
        conectividade_percent = (conectado_count / total_registros) * 100 if total_registros > 0 else 0
        
        # Encontrar limites de conectividade
        posicoes_conectadas = []
        posicoes_desconectadas = []
        
        for entry in data:
            pos = entry['position']
            if entry['ap_conectado'] == 'desconectado':
                posicoes_desconectadas.append(pos)
            else:
                posicoes_conectadas.append(pos)
        
        resultado = {
            'nome_teste': nome_teste,
            'total_registros': total_registros,
            'aps_conectados': aps_conectados,
            'handovers': handovers,
            'conectividade_percent': conectividade_percent,
            'conectado_count': conectado_count,
            'desconectado_count': desconectado_count,
            'posicoes_conectadas': posicoes_conectadas,
            'posicoes_desconectadas': posicoes_desconectadas,
            'dados_completos': data
        }
        
        print(f"   📊 Análise: {total_registros} registros, {handovers} handovers, {conectividade_percent:.1f}% conectado")
        return resultado
        
    except Exception as e:
        print(f"   ❌ Erro na análise: {e}")
        return None

def gerar_relatorio(resultados, nome_arquivo="RELATORIO_LIMITES_CONECTIVIDADE.md"):
    """Gera relatório completo dos testes"""
    
    with open(nome_arquivo, 'w') as f:
        f.write("# 📊 Relatório de Limites de Conectividade - DSL Mininet-WiFi\n\n")
        f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total de Testes:** {len(resultados)}\n\n")
        
        f.write("## 📋 Resumo Executivo\n\n")
        
        # Estatísticas gerais
        total_handovers = sum(r['handovers'] for r in resultados if r)
        total_conectividade = sum(r['conectividade_percent'] for r in resultados if r) / len(resultados) if resultados else 0
        
        f.write(f"- **Total de Handovers Detectados:** {total_handovers}\n")
        f.write(f"- **Conectividade Média:** {total_conectividade:.1f}%\n")
        f.write(f"- **Testes Realizados:** {len(resultados)}\n\n")
        
        f.write("## 🧪 Resultados Detalhados\n\n")
        
        for resultado in resultados:
            if not resultado:
                continue
                
            f.write(f"### Teste: {resultado['nome_teste']}\n\n")
            f.write(f"- **Registros:** {resultado['total_registros']}\n")
            f.write(f"- **Handovers:** {resultado['handovers']}\n")
            f.write(f"- **Conectividade:** {resultado['conectividade_percent']:.1f}%\n")
            f.write(f"- **APs Conectados:** {resultado['aps_conectados']}\n\n")
            
            if resultado['posicoes_conectadas']:
                f.write(f"- **Posições Conectadas:** {', '.join(resultado['posicoes_conectadas'][:5])}{'...' if len(resultado['posicoes_conectadas']) > 5 else ''}\n")
            if resultado['posicoes_desconectadas']:
                f.write(f"- **Posições Desconectadas:** {', '.join(resultado['posicoes_desconectadas'][:5])}{'...' if len(resultado['posicoes_desconectadas']) > 5 else ''}\n")
            
            f.write("\n")
        
        f.write("## 📈 Análise de Limites\n\n")
        
        # Análise de distâncias
        f.write("### Distâncias e Conectividade\n\n")
        for resultado in resultados:
            if not resultado:
                continue
                
            nome = resultado['nome_teste']
            if 'distancia' in nome:
                distancia = nome.split('_')[-1]
                f.write(f"- **Distância {distancia}:** {resultado['conectividade_percent']:.1f}% conectado\n")
        
        f.write("\n### Recomendações\n\n")
        f.write("1. **Para Handover Eficiente:** Usar distâncias menores entre APs\n")
        f.write("2. **Para Cobertura Máxima:** Ajustar potência de transmissão\n")
        f.write("3. **Para Testes Realistas:** Implementar modelo de propagação\n\n")
        
        f.write("---\n")
        f.write(f"*Relatório gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    print(f"\n📄 Relatório salvo em: {nome_arquivo}")

def main():
    """Função principal - executa série de testes"""
    
    print("🚀 Iniciando Testes de Limites de Conectividade")
    print("=" * 50)
    
    # Configurações de teste
    testes = [
        # Teste 1: APs muito próximos (5 unidades)
        {
            'nome': 'distancia_5',
            'ap1_x': 10.0,
            'ap2_x': 15.0,
            'start_x': 5.0,
            'end_x': 20.0
        },
        # Teste 2: APs médios (10 unidades)
        {
            'nome': 'distancia_10',
            'ap1_x': 10.0,
            'ap2_x': 20.0,
            'start_x': 5.0,
            'end_x': 25.0
        },
        # Teste 3: APs distantes (15 unidades)
        {
            'nome': 'distancia_15',
            'ap1_x': 10.0,
            'ap2_x': 25.0,
            'start_x': 5.0,
            'end_x': 30.0
        },
        # Teste 4: APs muito distantes (20 unidades)
        {
            'nome': 'distancia_20',
            'ap1_x': 10.0,
            'ap2_x': 30.0,
            'start_x': 5.0,
            'end_x': 35.0
        }
    ]
    
    resultados = []
    
    for i, teste in enumerate(testes, 1):
        print(f"\n🔬 Teste {i}/{len(testes)}")
        
        # Criar cenário
        cenario = criar_cenario_teste(
            ap1_x=teste['ap1_x'],
            ap2_x=teste['ap2_x'],
            start_x=teste['start_x'],
            end_x=teste['end_x']
        )
        
        # Executar teste
        sucesso = executar_teste(cenario, teste['nome'])
        
        if sucesso:
            # Aguardar um pouco para garantir que os logs foram salvos
            time.sleep(3)
            
            # Analisar resultados
            resultado = analisar_resultados(teste['nome'])
            resultados.append(resultado)
        else:
            resultados.append(None)
        
        # Limpar arquivo temporário
        try:
            os.remove(f"cenarios/temp_{teste['nome']}.json")
        except:
            pass
    
    # Gerar relatório
    print(f"\n📊 Gerando relatório final...")
    gerar_relatorio(resultados)
    
    print(f"\n✅ Testes concluídos! Verifique o relatório para análise detalhada.")

if __name__ == "__main__":
    main() 