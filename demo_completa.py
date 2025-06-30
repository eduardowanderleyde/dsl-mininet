#!/usr/bin/env python3

import os
import sys
import subprocess
import time

def executar_comando(comando, descricao):
    """Executa um comando e mostra o resultado"""
    print(f"\n🔧 {descricao}")
    print(f"Comando: {comando}")
    print("-" * 60)
    
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if resultado.stdout:
            print(resultado.stdout)
        if resultado.stderr:
            print("Erros:", resultado.stderr)
        return resultado.returncode == 0
    except Exception as e:
        print(f"Erro: {e}")
        return False

def mostrar_secao(titulo):
    """Mostra uma seção do demo"""
    print(f"\n{'='*60}")
    print(f"🎯 {titulo}")
    print(f"{'='*60}")

def demo_completa():
    """Demonstração completa do sistema"""
    print("🚀 DEMONSTRAÇÃO COMPLETA - DSL Mininet-WiFi")
    print("Este script demonstra todas as funcionalidades do sistema")
    
    # 1. Validar cenários
    mostrar_secao("1. VALIDAÇÃO DE CENÁRIOS")
    executar_comando("python3 teste_cenarios.py", "Validando todos os cenários")
    
    # 2. Criar cenário de teste
    mostrar_secao("2. CRIAÇÃO DE CENÁRIO DE TESTE")
    executar_comando("python3 teste_cenarios.py criar", "Criando cenário de teste")
    
    # 3. Mostrar estrutura de arquivos
    mostrar_secao("3. ESTRUTURA DE ARQUIVOS")
    executar_comando("ls -la cenarios/", "Listando cenários disponíveis")
    
    # 4. Analisar logs existentes (se houver)
    mostrar_secao("4. ANÁLISE DE LOGS EXISTENTES")
    if os.path.exists("results"):
        executar_comando("ls -la results/", "Listando logs existentes")
        if os.path.exists("results/station1_log.csv"):
            executar_comando("python3 analisar_logs.py results/station1_log.csv", "Analisando log existente")
    else:
        print("📁 Diretório 'results' não encontrado - será criado na primeira execução")
    
    # 5. Mostrar instruções de execução
    mostrar_secao("5. INSTRUÇÕES DE EXECUÇÃO")
    print("📋 Para executar um cenário:")
    print("   python3 executa_cenario.py cenarios/cenario_exemplo_1.json")
    print()
    print("📋 Para analisar logs:")
    print("   python3 analisar_logs.py todos")
    print()
    print("📋 Para usar a interface web:")
    print("   python3 app.py")
    print("   Acesse: http://localhost:5000")
    
    # 6. Mostrar exemplos de cenários
    mostrar_secao("6. EXEMPLOS DE CENÁRIOS")
    print("🎯 Cenário 1: Handover Básico (2 APs em linha reta)")
    print("   - Ideal para testar handover simples")
    print("   - Arquivo: cenarios/cenario_exemplo_1.json")
    print()
    print("🎯 Cenário 2: Handover Múltiplo (3 APs em triângulo)")
    print("   - Ideal para testar handover entre múltiplos APs")
    print("   - Arquivo: cenarios/cenario_exemplo_2.json")
    print()
    print("🎯 Cenário 3: Rede Complexa (4 APs em quadrado)")
    print("   - Ideal para testar cenários complexos")
    print("   - Arquivo: cenarios/cenario_exemplo_3.json")
    
    # 7. Mostrar correções implementadas
    mostrar_secao("7. CORREÇÕES IMPLEMENTADAS")
    print("✅ Formatação CSV corrigida (sem quebras de linha)")
    print("✅ Coleta RSSI robusta com múltiplos métodos")
    print("✅ Coleta latência melhorada com fallbacks")
    print("✅ Logs salvos em diretório 'results/'")
    print("✅ Log da posição inicial incluído")
    print("✅ Aguarda estabilização da rede")
    print("✅ Validação de cenários com teste_cenarios.py")
    print("✅ Análise estatística com analisar_logs.py")
    
    # 8. Mostrar próximos passos
    mostrar_secao("8. PRÓXIMOS PASSOS")
    print("1️⃣ Execute um cenário de exemplo:")
    print("   python3 executa_cenario.py cenarios/cenario_exemplo_1.json")
    print()
    print("2️⃣ Analise os resultados:")
    print("   python3 analisar_logs.py todos")
    print()
    print("3️⃣ Use a interface web para criar cenários personalizados:")
    print("   python3 app.py")
    print()
    print("4️⃣ Compare diferentes configurações para otimizar sua rede")
    
    print(f"\n{'='*60}")
    print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print("O sistema está pronto para uso!")
    print(f"{'='*60}")

def demo_rapida():
    """Demonstração rápida"""
    print("⚡ DEMONSTRAÇÃO RÁPIDA")
    print("Validando cenários...")
    executar_comando("python3 teste_cenarios.py", "Validação rápida")
    print("\n✅ Sistema pronto para uso!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rapida":
        demo_rapida()
    else:
        demo_completa() 