#!/usr/bin/env python3
"""
Script de teste para verificar a funcionalidade de execução no robô
"""

import requests
import json
import time

def testar_execucao_robo():
    """Testa a funcionalidade de execução no robô"""
    
    print("🤖 Testando Execução no Robô")
    print("=" * 50)
    
    # URL da interface
    base_url = "http://localhost:5000"
    
    # 1. Verificar se o servidor está rodando
    print("1. Verificando servidor...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando")
        else:
            print(f"❌ Servidor retornou status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro ao conectar no servidor: {e}")
        return
    
    # 2. Listar cenários disponíveis
    print("\n2. Listando cenários disponíveis...")
    try:
        response = requests.get(f"{base_url}/listar")
        if response.status_code == 200:
            cenarios = response.json()
            print(f"✅ Encontrados {len(cenarios)} cenários")
            for cenario in cenarios[:3]:  # Mostrar apenas os 3 primeiros
                print(f"   - {cenario}")
        else:
            print(f"❌ Erro ao listar cenários: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao listar cenários: {e}")
    
    # 3. Testar execução no robô
    print("\n3. Testando execução no robô...")
    cenario_teste = "cenario_teste_movimento_continuo.json"
    
    try:
        print(f"🎯 Testando cenário: {cenario_teste}")
        url_execucao = f"{base_url}/executar_robo/{cenario_teste}"
        
        print(f"📡 Fazendo requisição para: {url_execucao}")
        response = requests.get(url_execucao, timeout=30)
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Execução no robô iniciada com sucesso!")
            print("📋 Verifique a interface web para ver os logs detalhados")
            
            # Tentar extrair informações da resposta
            if "Raspberry Pi" in response.text:
                print("🔍 Detecção do Raspberry Pi encontrada na resposta")
            if "SSH" in response.text:
                print("🔍 Tentativa de conexão SSH detectada")
            if "USB" in response.text:
                print("🔍 Tentativa de conexão USB detectada")
                
        else:
            print(f"❌ Erro na execução: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout na requisição (pode ser normal se o robô está processando)")
    except Exception as e:
        print(f"❌ Erro ao testar execução: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Próximos passos:")
    print("1. Acesse: http://localhost:5000")
    print("2. Clique em 'Executar no Robô' em qualquer cenário")
    print("3. Verifique os logs de conexão com o Raspberry Pi")
    print("4. Monitore a execução em tempo real")

if __name__ == "__main__":
    testar_execucao_robo() 