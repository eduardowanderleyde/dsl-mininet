#!/usr/bin/env python3
import requests

print("🔍 Testando logs detalhados...")
response = requests.get("http://localhost:5000/executar_robo/cenario_teste_movimento_continuo.json")

if response.status_code == 200:
    print("✅ Requisição bem-sucedida!")
    content = response.text
    
    # Procurar por logs específicos
    markers = [
        "🆔 Sessão:", "🚀 Iniciando", "📋 Cenário:", "⏰ Início:",
        "🔗 Verificando", "✅ Conexão SSH", "💾 Verificando espaço",
        "📤 Enviando script", "📁 Tamanho do arquivo", "🔄 Iniciando upload",
        "✅ Script enviado", "🔍 Verificando arquivo", "📄 Arquivo criado",
        "🚀 Executando:", "⏳ Iniciando execução", "🔄 Preparando comando",
        "📝 Comando completo", "⚡ Executando comando", "⏱️ Comando executado",
        "✅ Comando executado", "📄 Saída do comando", "🆔 PID do processo"
    ]
    
    print("\n📋 Logs encontrados:")
    lines = content.split('\n')
    for line in lines:
        for marker in markers:
            if marker in line:
                print(f"  {line.strip()}")
                break
else:
    print(f"❌ Erro: {response.status_code}") 