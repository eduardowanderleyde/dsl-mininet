#!/usr/bin/env python3

import csv
import os
import sys
import statistics
from datetime import datetime

def analisar_log_csv(arquivo):
    """Analisa um arquivo de log CSV e retorna estatísticas"""
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
    
    # Extrair dados numéricos
    rssi_values = []
    latency_values = []
    
    for row in dados:
        try:
            rssi = float(row['rssi'].strip())
            rssi_values.append(rssi)
        except (ValueError, KeyError):
            pass
        
        try:
            latency = float(row['latency_ms'].strip())
            if latency < 9999:  # Ignorar timeouts
                latency_values.append(latency)
        except (ValueError, KeyError):
            pass
    
    # Calcular estatísticas
    stats = {
        'arquivo': arquivo,
        'total_registros': len(dados),
        'rssi': {
            'valores': rssi_values,
            'min': min(rssi_values) if rssi_values else None,
            'max': max(rssi_values) if rssi_values else None,
            'media': statistics.mean(rssi_values) if rssi_values else None,
            'mediana': statistics.median(rssi_values) if rssi_values else None
        },
        'latencia': {
            'valores': latency_values,
            'min': min(latency_values) if latency_values else None,
            'max': max(latency_values) if latency_values else None,
            'media': statistics.mean(latency_values) if latency_values else None,
            'mediana': statistics.median(latency_values) if latency_values else None
        }
    }
    
    return stats

def mostrar_estatisticas(stats):
    """Mostra as estatísticas de forma organizada"""
    if not stats:
        return
    
    print(f"\n📊 ANÁLISE: {os.path.basename(stats['arquivo'])}")
    print(f"📈 Total de registros: {stats['total_registros']}")
    
    # Estatísticas RSSI
    rssi = stats['rssi']
    if rssi['valores']:
        print(f"\n📶 RSSI (dBm):")
        print(f"   Mínimo: {rssi['min']:.1f}")
        print(f"   Máximo: {rssi['max']:.1f}")
        print(f"   Média: {rssi['media']:.1f}")
        print(f"   Mediana: {rssi['mediana']:.1f}")
        
        # Classificar qualidade do sinal
        media_rssi = rssi['media']
        if media_rssi >= -50:
            qualidade = "Excelente"
        elif media_rssi >= -60:
            qualidade = "Muito Boa"
        elif media_rssi >= -70:
            qualidade = "Boa"
        elif media_rssi >= -80:
            qualidade = "Regular"
        else:
            qualidade = "Ruim"
        print(f"   Qualidade: {qualidade}")
    else:
        print(f"\n📶 RSSI: Nenhum dado válido")
    
    # Estatísticas Latência
    lat = stats['latencia']
    if lat['valores']:
        print(f"\n⏱️  Latência (ms):")
        print(f"   Mínima: {lat['min']:.1f}")
        print(f"   Máxima: {lat['max']:.1f}")
        print(f"   Média: {lat['media']:.1f}")
        print(f"   Mediana: {lat['mediana']:.1f}")
        
        # Classificar qualidade da latência
        media_lat = lat['media']
        if media_lat <= 50:
            qualidade = "Excelente"
        elif media_lat <= 100:
            qualidade = "Muito Boa"
        elif media_lat <= 200:
            qualidade = "Boa"
        elif media_lat <= 500:
            qualidade = "Regular"
        else:
            qualidade = "Ruim"
        print(f"   Qualidade: {qualidade}")
    else:
        print(f"\n⏱️  Latência: Nenhum dado válido (possíveis timeouts)")

def analisar_todos_logs():
    """Analisa todos os logs CSV na pasta results"""
    results_dir = "results"
    
    if not os.path.exists(results_dir):
        print(f"❌ Diretório {results_dir} não encontrado")
        return
    
    arquivos_csv = [f for f in os.listdir(results_dir) if f.endswith('.csv')]
    
    if not arquivos_csv:
        print(f"❌ Nenhum arquivo CSV encontrado em {results_dir}")
        return
    
    print(f"🔍 Analisando {len(arquivos_csv)} arquivos de log...\n")
    
    for arquivo in sorted(arquivos_csv):
        caminho = os.path.join(results_dir, arquivo)
        stats = analisar_log_csv(caminho)
        if stats:
            mostrar_estatisticas(stats)
            print("-" * 60)

def mostrar_ultimos_registros(arquivo, n=5):
    """Mostra os últimos n registros de um arquivo CSV"""
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo {arquivo} não encontrado")
        return
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            dados = list(reader)
        
        print(f"\n📋 Últimos {min(n, len(dados))} registros de {os.path.basename(arquivo)}:")
        print("-" * 80)
        print(f"{'Timestamp':<20} {'Posição':<15} {'RSSI':<8} {'Latência':<10}")
        print("-" * 80)
        
        for row in dados[-n:]:
            timestamp = row.get('time', 'N/A')
            posicao = row.get('position', 'N/A')
            rssi = row.get('rssi', 'N/A')
            latencia = row.get('latency_ms', 'N/A')
            
            print(f"{timestamp:<20} {posicao:<15} {rssi:<8} {latencia:<10}")
            
    except Exception as e:
        print(f"❌ Erro ao ler arquivo {arquivo}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 analisar_logs.py todos                    # Analisa todos os logs")
        print("  python3 analisar_logs.py arquivo.csv              # Analisa arquivo específico")
        print("  python3 analisar_logs.py ultimos arquivo.csv [n]  # Mostra últimos n registros")
        return
    
    if sys.argv[1] == "todos":
        analisar_todos_logs()
    elif sys.argv[1] == "ultimos" and len(sys.argv) >= 3:
        arquivo = sys.argv[2]
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        mostrar_ultimos_registros(arquivo, n)
    elif len(sys.argv) >= 2:
        arquivo = sys.argv[1]
        stats = analisar_log_csv(arquivo)
        if stats:
            mostrar_estatisticas(stats)
            print("\n" + "="*60)
            mostrar_ultimos_registros(arquivo, 3)

if __name__ == "__main__":
    main() 