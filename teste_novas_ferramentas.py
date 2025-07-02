#!/usr/bin/env python3
"""
Teste das Novas Ferramentas Implementadas
Demonstra o uso do analisador de performance e gerador de relatórios
"""

import os
import sys
import subprocess
from datetime import datetime

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"🔧 {title}")
    print("="*60)

def print_section(title):
    """Imprime seção formatada"""
    print(f"\n📋 {title}")
    print("-" * 40)

def run_command(command, description):
    """Executa comando e mostra resultado"""
    print(f"\n🔄 {description}")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Sucesso!")
            if result.stdout.strip():
                print("Saída:")
                print(result.stdout)
        else:
            print("❌ Erro!")
            if result.stderr.strip():
                print("Erro:")
                print(result.stderr)
    except Exception as e:
        print(f"❌ Exceção: {e}")

def test_analisador_performance():
    """Testa o analisador de performance"""
    print_header("TESTE DO ANALISADOR DE PERFORMANCE")
    
    # Verificar se há dados para analisar
    if not os.path.exists("results"):
        print("❌ Diretório 'results' não encontrado!")
        print("💡 Execute primeiro um cenário para gerar dados")
        return False
    
    csv_files = [f for f in os.listdir("results") if f.endswith('.csv')]
    if not csv_files:
        print("❌ Nenhum arquivo CSV encontrado em 'results'!")
        print("💡 Execute primeiro um cenário para gerar dados")
        return False
    
    print(f"✅ Encontrados {len(csv_files)} arquivos CSV para análise")
    
    # Testar análise de cobertura
    print_section("Análise de Cobertura")
    run_command("python3 analisador_performance_avancado.py analyze --scenario cenario_exemplo_1", 
                "Analisando cobertura do cenário exemplo 1")
    
    # Testar detecção de anomalias
    print_section("Detecção de Anomalias")
    run_command("python3 analisador_performance_avancado.py anomalies --scenario cenario_exemplo_1", 
                "Detectando anomalias no cenário exemplo 1")
    
    # Testar geração de mapa de calor
    print_section("Mapa de Calor")
    run_command("python3 analisador_performance_avancado.py heatmap --scenario cenario_exemplo_1 --output teste_heatmap.png", 
                "Gerando mapa de calor do cenário exemplo 1")
    
    # Testar relatório completo
    print_section("Relatório Completo")
    run_command("python3 analisador_performance_avancado.py report --scenario cenario_exemplo_1 --output teste_relatorio.md", 
                "Gerando relatório completo do cenário exemplo 1")
    
    return True

def test_gerador_relatorios():
    """Testa o gerador de relatórios"""
    print_header("TESTE DO GERADOR DE RELATÓRIOS")
    
    # Verificar se há dados para analisar
    if not os.path.exists("results"):
        print("❌ Diretório 'results' não encontrado!")
        return False
    
    # Testar relatório HTML
    print_section("Relatório HTML")
    run_command("python3 gerador_relatorios.py html --scenario cenario_exemplo_1 --output teste_relatorio.html", 
                "Gerando relatório HTML do cenário exemplo 1")
    
    # Testar relatório Excel
    print_section("Relatório Excel")
    run_command("python3 gerador_relatorios.py excel --scenario cenario_exemplo_1 --output teste_relatorio.xlsx", 
                "Gerando relatório Excel do cenário exemplo 1")
    
    return True

def test_interface_web_atualizada():
    """Testa a interface web atualizada"""
    print_header("TESTE DA INTERFACE WEB ATUALIZADA")
    
    print_section("Verificação da Interface Web")
    
    # Verificar se app.py foi atualizado
    if os.path.exists("app.py"):
        with open("app.py", "r") as f:
            content = f.read()
            if "executa_cenario_mesh_v3.py" in content:
                print("✅ Interface web atualizada para usar versão 3!")
            else:
                print("⚠️ Interface web ainda usa versão antiga")
    else:
        print("❌ Arquivo app.py não encontrado!")
    
    # Verificar se templates existem
    if os.path.exists("templates"):
        templates = os.listdir("templates")
        print(f"✅ Templates encontrados: {len(templates)} arquivos")
        for template in templates:
            print(f"  - {template}")
    else:
        print("❌ Diretório templates não encontrado!")
    
    return True

def test_instalacao_dependencias():
    """Testa se as dependências estão instaladas"""
    print_header("TESTE DE DEPENDÊNCIAS")
    
    required_packages = [
        "pandas", "numpy", "matplotlib", "seaborn", "openpyxl", "jinja2"
    ]
    
    print_section("Verificando Dependências")
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - Instalado")
        except ImportError:
            print(f"❌ {package} - Não instalado")
            return False
    
    print("\n💡 Para instalar dependências faltantes:")
    print("pip install pandas numpy matplotlib seaborn openpyxl jinja2")
    
    return True

def criar_dados_teste():
    """Cria dados de teste se não existirem"""
    print_header("CRIAÇÃO DE DADOS DE TESTE")
    
    if os.path.exists("results") and any(f.endswith('.csv') for f in os.listdir("results")):
        print("✅ Dados de teste já existem")
        return True
    
    print("📝 Criando dados de teste...")
    
    # Criar diretório results
    os.makedirs("results", exist_ok=True)
    
    # Criar dados de teste simulados
    import pandas as pd
    import numpy as np
    
    # Dados para station 1
    data1 = {
        'time': pd.date_range('2025-01-01 10:00:00', periods=10, freq='3S'),
        'position': ['"5.0,20.0"', '"15.0,20.0"', '"25.0,20.0"', '"35.0,20.0"', '"45.0,20.0"',
                    '"55.0,20.0"', '"65.0,20.0"', '"75.0,20.0"', '"85.0,20.0"', '"95.0,20.0"'],
        'rssi': [-100, -36, -36, -36, -45, -52, -58, -65, -72, -78],
        'latency_ms': [0.023, 0.028, 0.015, 0.041, 0.035, 0.042, 0.048, 0.055, 0.062, 0.068],
        'jitter_ms': [0.002, 0.003, 0.001, 0.004, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008],
        'packet_loss_percent': [0.0, 0.0, 0.0, 0.0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2],
        'connected_ap': ['none', 'ap1', 'ap1', 'ap1', 'ap1', 'ap2', 'ap2', 'ap2', 'ap2', 'ap2']
    }
    
    df1 = pd.DataFrame(data1)
    df1.to_csv("results/cenario_exemplo_1_sta1.csv", index=False)
    
    # Dados para station 2
    data2 = {
        'time': pd.date_range('2025-01-01 10:00:00', periods=8, freq='3S'),
        'position': ['"10.0,30.0"', '"20.0,30.0"', '"30.0,30.0"', '"40.0,30.0"',
                    '"50.0,30.0"', '"60.0,30.0"', '"70.0,30.0"', '"80.0,30.0"'],
        'rssi': [-45, -38, -42, -48, -55, -62, -68, -75],
        'latency_ms': [0.032, 0.028, 0.035, 0.041, 0.048, 0.055, 0.062, 0.068],
        'jitter_ms': [0.003, 0.002, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009],
        'packet_loss_percent': [0.0, 0.0, 0.1, 0.2, 0.4, 0.6, 0.9, 1.3],
        'connected_ap': ['ap1', 'ap1', 'ap1', 'ap2', 'ap2', 'ap2', 'ap2', 'ap2']
    }
    
    df2 = pd.DataFrame(data2)
    df2.to_csv("results/cenario_exemplo_1_sta2.csv", index=False)
    
    print("✅ Dados de teste criados:")
    print("  - results/cenario_exemplo_1_sta1.csv (10 registros)")
    print("  - results/cenario_exemplo_1_sta2.csv (8 registros)")
    
    return True

def main():
    """Função principal"""
    print("🚀 TESTE DAS NOVAS FERRAMENTAS IMPLEMENTADAS")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Teste 1: Dependências
    if not test_instalacao_dependencias():
        print("\n❌ Dependências não estão instaladas!")
        print("💡 Execute: pip install -r requirements.txt")
        return
    
    # Teste 2: Criar dados de teste se necessário
    criar_dados_teste()
    
    # Teste 3: Analisador de Performance
    test_analisador_performance()
    
    # Teste 4: Gerador de Relatórios
    test_gerador_relatorios()
    
    # Teste 5: Interface Web
    test_interface_web_atualizada()
    
    print_header("RESUMO DOS TESTES")
    print("✅ Testes concluídos!")
    print("\n📁 Arquivos gerados:")
    
    generated_files = []
    for file in os.listdir("."):
        if file.startswith("teste_") or file.startswith("heatmap_") or file.startswith("report_"):
            generated_files.append(file)
    
    if generated_files:
        for file in generated_files:
            print(f"  - {file}")
    else:
        print("  - Nenhum arquivo de teste gerado")
    
    print("\n🎯 Próximos passos:")
    print("1. Abra os relatórios HTML gerados no navegador")
    print("2. Analise os mapas de calor PNG")
    print("3. Abra os relatórios Excel no LibreOffice/Excel")
    print("4. Use a interface web atualizada: python3 app.py")
    
    print("\n💡 Para mais informações, consulte:")
    print("- SUGESTOES_MELHORIAS_FERRAMENTAS.md")
    print("- analisador_performance_avancado.py --help")
    print("- gerador_relatorios.py --help")

if __name__ == "__main__":
    main() 