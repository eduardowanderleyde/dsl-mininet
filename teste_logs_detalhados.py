#!/usr/bin/env python3
"""
Teste dos logs detalhados
"""

import requests
import json
import time

def testar_logs_detalhados():
    print("🔍 Testando logs detalhados...")
    
    # Testar execução no robô
    url = "http://localhost:5000/executar_robo/cenario_teste_movimento_continuo.json"
    
    print(f"📡 Fazendo requisição para: {url}")
    response = requests.get(url)
    
    if response.status_code == 200:
        print("✅ Requisição bem-sucedida!")
        
        # Extrair informações do HTML
        html_content = response.text
        
        # Procurar por informações específicas
        if "🆔 Sessão:" in html_content:
            print("✅ Sessão ID encontrada!")
            
            # Extrair session ID
            import re
            session_match = re.search(r'🆔 Sessão: ([a-f0-9]+)', html_content)
            if session_match:
                session_id = session_match.group(1)
                print(f"🆔 Session ID: {session_id}")
                
                # Testar monitoramento
                print("🔄 Testando monitoramento...")
                monitor_url = f"http://localhost:5000/monitorar_execucao/{session_id}"
                monitor_response = requests.get(monitor_url)
                
                if monitor_response.status_code == 200:
                    monitor_data = monitor_response.json()
                    print("✅ Monitoramento funcionando!")
                    print(f"📊 Processo ativo: {monitor_data.get('processo_ativo', 'N/A')}")
                    print(f"⏰ Timestamp: {monitor_data.get('timestamp', 'N/A')}")
                else:
                    print(f"❌ Erro no monitoramento: {monitor_response.status_code}")
        
        if "🆔 PID do processo:" in html_content:
            print("✅ PID encontrado!")
            
        if "📊 Log file:" in html_content:
            print("✅ Log file especificado!")
            
        if "⏱️ Tempo de execução:" in html_content:
            print("✅ Tempo de execução registrado!")
            
        print("\n📋 Logs encontrados:")
        
        # Procurar pela seção de logs
        if '<pre class="bg-light p-3 rounded"' in html_content:
            start = html_content.find('<pre class="bg-light p-3 rounded"')
            end = html_content.find('</pre>', start)
            if start != -1 and end != -1:
                log_section = html_content[start:end]
                # Extrair apenas o texto dentro do pre
                log_text = log_section.split('>', 1)[1] if '>' in log_section else log_section
                log_lines = log_text.split('\n')
                
                for line in log_lines:
                    if any(marker in line for marker in ['🆔', '📊', '⏱️', '🔍', '✅', '❌', '🚀', '📤', '🔗']):
                        print(f"  {line.strip()}")
        else:
            print("  ❌ Seção de logs não encontrada")
    else:
        print(f"❌ Erro na requisição: {response.status_code}")

if __name__ == "__main__":
    testar_logs_detalhados() 