# DSL Mininet-WiFi

Sistema para criar, configurar e executar cenários de rede usando Mininet-WiFi com interface web.

## 🚀 Funcionalidades

- **Interface Web**: Criação e gerenciamento de cenários via Flask
- **DSL JSON**: Configuração de cenários através de arquivos JSON
- **Execução Remota**: Execução de cenários em VM Mininet-WiFi via SSH
- **Logs CSV**: Geração automática de logs com RSSI e latência
- **Análise de Dados**: Scripts para análise dos resultados

## 📁 Estrutura do Projeto

```
dsl-mininet/
├── app.py                 # Aplicação Flask
├── executa_cenario.py     # Script principal de execução (CORRIGIDO)
├── teste_cenarios.py      # Validador de cenários
├── analisar_logs.py       # Analisador de logs CSV
├── cenarios/              # Cenários de exemplo
│   ├── cenario_exemplo_1.json  # 2 APs em linha reta
│   ├── cenario_exemplo_2.json  # 3 APs em triângulo
│   └── cenario_exemplo_3.json  # 4 APs em quadrado
├── results/               # Logs gerados
├── templates/             # Templates HTML
└── Dockerfile            # Containerização
```

## 🔧 Correções Implementadas

### 1. Script de Execução (`executa_cenario.py`)
- ✅ **Formatação CSV**: Corrigido problema de quebras de linha nos valores
- ✅ **Coleta RSSI**: Implementada coleta robusta usando múltiplos métodos
- ✅ **Coleta Latência**: Melhorada detecção de latência com fallbacks
- ✅ **Diretório Results**: Logs salvos automaticamente em `results/`
- ✅ **Posição Inicial**: Log da posição inicial antes da movimentação
- ✅ **Estabilização**: Aguarda estabilização da rede antes de coletar dados

### 2. Cenários de Exemplo
- ✅ **Cenário 1**: 2 APs em linha reta + 1 station (handover básico)
- ✅ **Cenário 2**: 3 APs em triângulo + 1 station (handover múltiplo)
- ✅ **Cenário 3**: 4 APs em quadrado + 2 stations (cenário complexo)

### 3. Scripts de Análise
- ✅ **Validação**: `teste_cenarios.py` valida estrutura dos cenários
- ✅ **Análise**: `analisar_logs.py` analisa logs CSV com estatísticas
- ✅ **Preview**: Visualização detalhada dos cenários

## 🎯 Como Usar

### 1. Testar Cenários
```bash
# Validar todos os cenários
python3 teste_cenarios.py

# Criar cenário de teste
python3 teste_cenarios.py criar
```

### 2. Executar Cenário
```bash
# Executar cenário específico
python3 executa_cenario.py cenarios/cenario_exemplo_1.json
```

### 3. Analisar Logs
```bash
# Analisar todos os logs
python3 analisar_logs.py todos

# Analisar arquivo específico
python3 analisar_logs.py results/sta1_log.csv

# Ver últimos registros
python3 analisar_logs.py ultimos results/sta1_log.csv 5
```

### 4. Interface Web
```bash
# Executar Flask
python3 app.py

# Acessar: http://localhost:5000
```

## 📊 Formato dos Logs CSV

Os logs são gerados em `results/` com o formato:

```csv
time,position,rssi,latency_ms
2025-06-30 19:05:55,"25.0,15.0",-36,45.2
2025-06-30 19:05:58,"20.0,25.0",-42,67.8
2025-06-30 19:06:01,"15.0,15.0",-38,52.1
```

### Campos:
- **time**: Timestamp da medição
- **position**: Coordenadas X,Y da station
- **rssi**: Força do sinal em dBm (valores mais próximos de 0 são melhores)
- **latency_ms**: Latência em milissegundos

## 🎯 Cenários de Exemplo

### Cenário 1: Handover Básico
- **2 APs** em linha reta (10,20) e (30,20)
- **1 Station** movendo-se entre eles
- **Ideal para**: Testar handover simples

### Cenário 2: Handover Múltiplo
- **3 APs** em triângulo
- **1 Station** movendo-se em trajetória triangular
- **Ideal para**: Testar handover entre múltiplos APs

### Cenário 3: Rede Complexa
- **4 APs** em quadrado
- **2 Stations** com trajetórias diferentes
- **Ideal para**: Testar cenários complexos com múltiplas stations

## 🔍 Análise de Qualidade

### RSSI (Força do Sinal)
- **-50 a 0 dBm**: Excelente
- **-60 a -50 dBm**: Muito Boa
- **-70 a -60 dBm**: Boa
- **-80 a -70 dBm**: Regular
- **< -80 dBm**: Ruim

### Latência
- **< 50ms**: Excelente
- **50-100ms**: Muito Boa
- **100-200ms**: Boa
- **200-500ms**: Regular
- **> 500ms**: Ruim

## 🐳 Docker

```bash
# Construir imagem
docker build -t dsl-mininet .

# Executar container
docker run -p 5000:5000 dsl-mininet
```

## 🔧 Configuração SSH

Para execução remota, configure o acesso SSH na VM Mininet-WiFi:

```bash
# Na VM Mininet-WiFi
sudo usermod -aG sudo $USER
echo "$USER ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/$USER
```

## 📝 Próximos Passos

1. **Execute um cenário de exemplo**:
   ```bash
   python3 executa_cenario.py cenarios/cenario_exemplo_1.json
   ```

2. **Analise os resultados**:
   ```bash
   python3 analisar_logs.py todos
   ```

3. **Use a interface web** para criar cenários personalizados

4. **Compare diferentes configurações** para otimizar sua rede

## 🆘 Solução de Problemas

### Erro de Módulo Mininet-WiFi
```bash
# Reinstalar Mininet-WiFi para Python 3
cd ~/mininet-wifi
sudo python3.12 setup.py install
```

### Logs com Formatação Ruim
- ✅ **Corrigido**: Script atualizado gera CSV limpo
- ✅ **Validação**: Use `teste_cenarios.py` para verificar cenários

### Latência Alta (9999ms)
- Verificar conectividade da rede
- Ajustar posições dos APs
- Verificar configurações de potência

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs de execução
2. Use `teste_cenarios.py` para validar cenários
3. Use `analisar_logs.py` para analisar resultados
4. Consulte os exemplos fornecidos 

# DSL Mininet-WiFi + Execução em Robô Real

## 🚦 Fluxo Completo do Sistema

### 🎛️ Etapa de Orquestração (Flask)
- 💻 Interface web funcionando
- ✅ Endpoint `/executar_robo/<cenario>` respondendo 200
- 🚀 Upload e início do script confirmados
- 💬 Logs completos no backend (PID, status, confirmação)

### 🤖 Etapa no Raspberry Pi
- 📂 Script transferido e salvo
- ✅ Script executado via SSH
- 🔥 PID validado
- 📝 Log do script em arquivo (`robo_output_<sessao>.log`)
- 🎥 Monitoramento possível em tempo real (via tail ou scp)

---

## 🛠️ Próximos Passos para Depuração

1. **Acessar o Raspberry Pi via SSH**
   ```bash
   ssh eduardowanderley@192.168.68.107
   ```
2. **Ver log do script em tempo real**
   ```bash
   tail -f robo_output_<sessao>.log
   ```
3. **(Opcional) Executar manualmente para ver traceback**
   ```bash
   python3 robo_script_cenario_quarto_final.py
   ```
4. **(Opcional) Baixar log para o Mac**
   ```bash
   scp eduardowanderley@192.168.68.107:/home/eduardowanderley/robo_output_<sessao>.log ~/Downloads
   open ~/Downloads/robo_output_<sessao>.log
   ```

---

## 💡 Dicas de Depuração
- Verifique dependências no Pi (`pip install ...`)
- Confira permissões (`chmod +x` ou execute com `python3`)
- Teste hardware (USB, motores, sensores)
- Veja o traceback no log/manual

---

## 💬 O que posso te ajudar:
- ✅ Revisar o script `robo_script_cenario_quarto_final.py`
- ✅ Sugerir melhorias no log (timestamps, formatação, status em JSON)
- ✅ Criar script de coleta automática dos logs para o Mac
- ✅ Criar um "monitor ao vivo" no Flask mostrando progresso

---

**Parabéns pelo fluxo, está super profissional! 🚀** 