#!/usr/bin/env python3
"""
Script para analisar logs do Raspberry Pi móvel
Analisa dados coletados em tempo real durante o movimento
"""

import csv
import os
import sys
from datetime import datetime

def analisar_log_raspberry(arquivo_log):
    """Analisa log do Raspberry Pi móvel"""
    
    if not os.path.exists(arquivo_log):
        print(f"❌ Arquivo não encontrado: {arquivo_log}")
        return None
    
    try:
        with open(arquivo_log, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            dados = list(reader)
        
        if not dados:
            print(f"❌ Arquivo vazio: {arquivo_log}")
            return None
        
        print(f"🤖 ANÁLISE DO RASPBERRY PI MÓVEL")
        print(f"📁 Arquivo: {arquivo_log}")
        print(f"📊 Total de registros: {len(dados)}")
        print("=" * 60)
        
        # Análise básica
        aps_conectados = {}
        handovers = 0
        posicoes_visitadas = []
        rssi_total = 0
        latencia_total = 0
        registros_conectados = 0
        
        ap_anterior = None
        for i, registro in enumerate(dados):
            # Contar APs
            ap = registro.get('ap_conectado', 'desconectado')
            if ap not in aps_conectados:
                aps_conectados[ap] = 0
            aps_conectados[ap] += 1
            
            # Contar handovers
            if ap_anterior and ap_anterior != ap and ap != 'desconectado':
                handovers += 1
            ap_anterior = ap
            
            # Coletar posições
            pos = f"({registro.get('x', 'N/A')}, {registro.get('y', 'N/A')})"
            if pos not in posicoes_visitadas:
                posicoes_visitadas.append(pos)
            
            # Estatísticas de RSSI e latência
            try:
                rssi = int(registro.get('rssi_dbm', -100))
                latencia = float(registro.get('latencia_ms', 9999))
                
                if ap != 'desconectado':
                    rssi_total += rssi
                    latencia_total += latencia
                    registros_conectados += 1
            except (ValueError, TypeError):
                continue
        
        # Calcular médias
        rssi_medio = rssi_total / registros_conectados if registros_conectados > 0 else 0
        latencia_media = latencia_total / registros_conectados if registros_conectados > 0 else 0
        
        # Exibir resultados
        print(f"\n📡 APs CONECTADOS:")
        for ap, count in aps_conectados.items():
            porcentagem = (count / len(dados)) * 100
            print(f"   • {ap}: {count} vezes ({porcentagem:.1f}%)")
        
        print(f"\n🔄 HANDOVERS DETECTADOS: {handovers}")
        
        print(f"\n📍 POSIÇÕES VISITADAS ({len(posicoes_visitadas)}):")
        for i, pos in enumerate(posicoes_visitadas, 1):
            print(f"   {i}. {pos}")
        
        print(f"\n📊 ESTATÍSTICAS DE QUALIDADE:")
        print(f"   • RSSI Médio: {rssi_medio:.1f} dBm")
        print(f"   • Latência Média: {latencia_media:.2f} ms")
        print(f"   • Conectividade: {registros_conectados}/{len(dados)} ({registros_conectados/len(dados)*100:.1f}%)")
        
        # Análise detalhada por posição
        print(f"\n📋 ANÁLISE DETALHADA POR POSIÇÃO:")
        print("-" * 80)
        print(f"{'Posição':<15} {'RSSI':<8} {'Latência':<10} {'AP':<12} {'Handover':<10}")
        print("-" * 80)
        
        ap_anterior = None
        for registro in dados:
            pos = f"({registro.get('x', 'N/A')}, {registro.get('y', 'N/A')})"
            rssi = registro.get('rssi_dbm', 'N/A')
            latencia = registro.get('latencia_ms', 'N/A')
            ap = registro.get('ap_conectado', 'N/A')
            
            # Detectar handover
            handover = "Sim" if ap_anterior and ap_anterior != ap and ap != 'desconectado' else "Não"
            
            print(f"{pos:<15} {rssi:<8} {latencia:<10} {ap:<12} {handover:<10}")
            ap_anterior = ap
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        if handovers == 0:
            print("   ⚠️  Nenhum handover detectado - considere:")
            print("      • Reduzir distância entre APs")
            print("      • Ajustar potência de transmissão")
            print("      • Forçar desconexão/reconexão")
        
        if rssi_medio < -70:
            print("   ⚠️  RSSI baixo - considere:")
            print("      • Aproximar APs")
            print("      • Aumentar potência")
            print("      • Verificar obstáculos")
        
        if latencia_media > 100:
            print("   ⚠️  Latência alta - considere:")
            print("      • Verificar qualidade da rede")
            print("      • Otimizar configurações")
            print("      • Verificar interferência")
        
        return {
            'total_registros': len(dados),
            'handovers': handovers,
            'aps_conectados': aps_conectados,
            'rssi_medio': rssi_medio,
            'latencia_media': latencia_media,
            'conectividade_percent': (registros_conectados/len(dados)*100) if len(dados) > 0 else 0
        }
        
    except Exception as e:
        print(f"❌ Erro ao analisar arquivo: {e}")
        return None

def listar_logs_raspberry():
    """Lista todos os logs do Raspberry Pi disponíveis"""
    results_dir = 'results'
    
    if not os.path.exists(results_dir):
        print("❌ Diretório 'results' não encontrado")
        return []
    
    logs_raspberry = []
    for arquivo in os.listdir(results_dir):
        if arquivo.startswith('raspberry_pi_') and arquivo.endswith('_log.csv'):
            logs_raspberry.append(os.path.join(results_dir, arquivo))
    
    return logs_raspberry

def main():
    """Função principal"""
    
    if len(sys.argv) == 1:
        # Sem argumentos - listar logs disponíveis
        logs = listar_logs_raspberry()
        
        if not logs:
            print("🤖 Nenhum log do Raspberry Pi encontrado")
            print("💡 Execute primeiro: sudo python3 executa_raspberry_movel.py cenarios/cenario_raspberry_movel.json")
            return
        
        print("🤖 Logs do Raspberry Pi disponíveis:")
        for i, log in enumerate(logs, 1):
            print(f"   {i}. {os.path.basename(log)}")
        
        print(f"\n💡 Para analisar um log específico:")
        print(f"   python3 analisar_raspberry_pi.py <arquivo_log>")
        print(f"   Exemplo: python3 analisar_raspberry_pi.py {logs[0]}")
        
        # Analisar o primeiro log automaticamente
        if logs:
            print(f"\n📊 Analisando automaticamente: {os.path.basename(logs[0])}")
            analisar_log_raspberry(logs[0])
    
    elif len(sys.argv) == 2:
        # Analisar arquivo específico
        arquivo_log = sys.argv[1]
        analisar_log_raspberry(arquivo_log)
    
    else:
        print("🤖 Uso: python3 analisar_raspberry_pi.py [arquivo_log]")
        print("📋 Se não especificar arquivo, lista todos os logs disponíveis")

if __name__ == "__main__":
    main() 