#!/usr/bin/env python3

import csv
import os
import sys
import json
from datetime import datetime

def analisar_log_mesh(arquivo):
    """Analisa um arquivo de log de mesh"""
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo {arquivo} não encontrado")
        return None
    
    dados = []
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dados.append(row)
    except Exception as e:
        print(f"❌ Erro ao ler arquivo {arquivo}: {e}")
        return None
    
    if not dados:
        print(f"⚠️  Arquivo {arquivo} está vazio")
        return None
    
    return dados

def mostrar_analise_mesh(dados, nome_arquivo):
    """Mostra análise detalhada dos dados de mesh"""
    if not dados:
        return
    
    print(f"\n📊 ANÁLISE MESH: {nome_arquivo}")
    print(f"📈 Total de registros: {len(dados)}")
    
    # Análise de APs conectados
    aps_conectados = {}
    for row in dados:
        ap = row.get('ap_conectado', 'desconectado')
        if ap in aps_conectados:
            aps_conectados[ap] += 1
        else:
            aps_conectados[ap] = 1
    
    print(f"\n📡 APs Conectados:")
    for ap, count in aps_conectados.items():
        porcentagem = (count / len(dados)) * 100
        print(f"  • {ap}: {count} vezes ({porcentagem:.1f}%)")
    
    # Análise de handovers
    handovers = 0
    ap_anterior = None
    for row in dados:
        ap_atual = row.get('ap_conectado', 'desconectado')
        if ap_anterior and ap_anterior != ap_atual and ap_atual != 'desconectado':
            handovers += 1
        ap_anterior = ap_atual
    
    print(f"\n🔄 Handovers detectados: {handovers}")
    
    # Análise de conectividade
    conectado = sum(1 for row in dados if row.get('ap_conectado') != 'desconectado')
    desconectado = len(dados) - conectado
    print(f"\n📶 Conectividade:")
    print(f"  • Conectado: {conectado} registros ({conectado/len(dados)*100:.1f}%)")
    print(f"  • Desconectado: {desconectado} registros ({desconectado/len(dados)*100:.1f}%)")

def analisar_topologia_mesh(arquivo):
    """Analisa arquivo de topologia mesh"""
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo {arquivo} não encontrado")
        return
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            dados = list(reader)
        
        if dados:
            print(f"\n🌐 TOPOLOGIA MESH: {arquivo}")
            for row in dados:
                print(f"⏰ Timestamp: {row.get('time', 'N/A')}")
                print(f"🔗 Links: {row.get('links', 'N/A')}")
                print(f"📋 Topologia: {row.get('topology', 'N/A')[:100]}...")
        else:
            print(f"⚠️  Arquivo {arquivo} está vazio")
            
    except Exception as e:
        print(f"❌ Erro ao ler arquivo {arquivo}: {e}")

def analisar_todos_mesh():
    """Analisa todos os logs de mesh"""
    results_dir = "results"
    
    if not os.path.exists(results_dir):
        print(f"❌ Diretório {results_dir} não encontrado")
        return
    
    # Procurar arquivos de mesh
    arquivos_mesh = [f for f in os.listdir(results_dir) if 'mesh' in f.lower() and f.endswith('.csv')]
    
    if not arquivos_mesh:
        print(f"❌ Nenhum arquivo de mesh encontrado em {results_dir}")
        return
    
    print(f"🔍 Analisando {len(arquivos_mesh)} arquivos de mesh...\n")
    
    for arquivo in sorted(arquivos_mesh):
        caminho = os.path.join(results_dir, arquivo)
        
        if 'topology' in arquivo.lower():
            analisar_topologia_mesh(caminho)
        else:
            dados = analisar_log_mesh(caminho)
            if dados:
                mostrar_analise_mesh(dados, arquivo)
        
        print("-" * 60)

def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 analisar_mesh.py todos                    # Analisa todos os logs de mesh")
        print("  python3 analisar_mesh.py arquivo.csv              # Analisa arquivo específico")
        return
    
    if sys.argv[1] == "todos":
        analisar_todos_mesh()
    elif len(sys.argv) >= 2:
        arquivo = sys.argv[1]
        if 'topology' in arquivo.lower():
            analisar_topologia_mesh(arquivo)
        else:
            dados = analisar_log_mesh(arquivo)
            if dados:
                mostrar_analise_mesh(dados, arquivo)

if __name__ == "__main__":
    main() 