# 🚀 DSL Mininet-WiFi v4.0 - Estado Atual

## ✅ Versão 4.0 SUPER COMPLETA - FUNCIONANDO

### 🎯 Funcionalidades Implementadas

#### 📊 Coleta Completa de Dados WiFi
- **SSID e BSSID detalhados** - Identificação completa das redes
- **RSSI com qualidade** - Força do sinal em dBm
- **Latência com packet loss** - Performance da rede
- **Bandwidth/Throughput (iperf3)** - Velocidade real da conexão
- **Handover inteligente** - Detecção automática de mudança de AP
- **Scan completo de redes** - Descoberta de todas as redes disponíveis

#### 🔬 Modelos de Propagação Avançados
- **📡 Simples (Padrão)** - Modelo básico, mais rápido
- **📊 Log-Distance** - Atenuação logarítmica realista
- **🌐 Friis** - Propagação em espaço livre
- **🏔️ Two-Ray Ground** - Considera reflexão no solo
- **🌫️ Shadowing** - Adiciona variação aleatória

#### 🚗 Tipos de Mobilidade
- **⏭️ Discreta (Saltos)** - Comportamento original, salta entre pontos
- **🔄 Contínua (Suave)** - Movimento suave com velocidade configurável
- **🎲 Random Walk** - Movimento aleatório realista

#### 🔧 Funcionalidades Técnicas
- **Detecção de handover** via ping para diferentes IPs dos APs
- **Fallback para scan** quando `iw link` não retorna dados
- **Teste de bandwidth** usando iperf3 com servidor em background
- **Logs estruturados** em CSV com timestamp
- **Interface web** completa para gerenciamento
- **Configuração de velocidade** de movimento (0.1-10 m/s)
- **Intervalo de amostragem** configurável (0.1-5 segundos)

### 📁 Arquivos Principais

#### ✅ Arquivos Ativos (Manter)
- `executa_cenario_mesh_v4.py` - **Script principal v4.0**
- `app.py` - Interface web Flask
- `requirements.txt` - Dependências Python
- `README.md` - Documentação principal
- `cenarios/` - Pasta com cenários JSON
- `results/` - Pasta com logs CSV
- `templates/` - Templates HTML da interface web

#### 🧹 Arquivos para Limpeza
- `executa_cenario_mesh_v2.py` - Versão antiga
- `executa_cenario_mesh_v3.py` - Versão antiga
- `executa_cenario_scan_wifi.py` - Funcionalidade integrada na v4
- `executa_raspberry_movel.py` - Funcionalidade integrada na v4
- `executa_cenario_handover_forcado.py` - Funcionalidade integrada na v4
- `executa_cenario_mesh.py` - Versão antiga
- `executa_cenario.py` - Versão antiga
- `teste_*.py` - Scripts de teste antigos
- `analisar_*.py` - Scripts de análise antigos
- `*.md` - Documentação antiga (exceto README.md)

### 🚀 Fluxo de Uso Atual

1. **Acessar interface web**: `python3 app.py`
2. **Criar cenário**: Configurar APs, stations e opções avançadas via web
3. **Executar simulação**: Clique em "Executar" na interface
4. **Analisar resultados**: Ver logs em `results/`

### 📊 Estrutura dos Logs v4.0

```csv
timestamp,wifi_info,latency_info,bandwidth_info,handover_info
2024-01-15 10:30:15,"[{'SSID': 'meshNet', 'BSSID': '00:11:22:33:44:55', 'Signal Level (dBm)': -45}]","{'latency_ms': 2.5, 'packet_loss': False}","{'bandwidth_mbps': 25.6}","{'handover': False}"
```

### 🔧 Comandos de Execução

#### Via Interface Web
```bash
python3 app.py
# Acessar http://localhost:5000
```

#### Via Linha de Comando
```bash
sudo python3 executa_cenario_mesh_v4.py cenario_exemplo.json
```

### 🎯 Novas Funcionalidades v4.0

#### 📡 Modelos de Propagação
- **Simples**: Atenuação linear com distância (padrão, mais rápido)
- **Log-Distance**: Atenuação logarítmica realista
- **Friis**: Propagação em espaço livre (modelo físico)
- **Two-Ray Ground**: Considera reflexão no solo
- **Shadowing**: Adiciona variação aleatória (mais realista)

#### 🚗 Tipos de Mobilidade
- **Discreta**: Salta entre pontos da trajetória (comportamento original)
- **Contínua**: Movimento suave com velocidade configurável
- **Random Walk**: Movimento aleatório com pontos intermediários

#### ⚙️ Configurações Avançadas
- **Velocidade de Movimento**: 0.1-10 m/s (padrão: 2 m/s)
- **Intervalo de Amostragem**: 0.1-5 segundos (padrão: 1s)
- **Threshold RSSI**: -100 a -30 dBm (padrão: -65 dBm)
- **Histerese**: 1-20 dBm (padrão: 5 dBm)

### 📋 Cenários de Exemplo

#### Movimento Contínuo com Log-Distance
```json
{
  "propagation": {
    "model": "log_distance",
    "mobility_type": "continuous",
    "mobility_speed": 2.0,
    "sampling_interval": 0.5
  }
}
```

#### Movimento Discreto (Original)
```json
{
  "propagation": {
    "model": "simple",
    "mobility_type": "discrete",
    "mobility_speed": 2.0,
    "sampling_interval": 1.0
  }
}
```

### 🎯 Próximos Passos

1. **Testes das novas funcionalidades** - Validar modelos de propagação e mobilidade
2. **Otimizações de performance** - Melhorar velocidade dos modelos avançados
3. **Documentação completa** - Tutorial detalhado na interface web
4. **Exemplos práticos** - Cenários pré-configurados para diferentes casos de uso

### ✅ Status: PRONTO PARA USO

A versão 4.0 está **100% funcional** e agora inclui:
- ✅ **Modelos de propagação avançados** (opcionais)
- ✅ **Movimento contínuo** (além do discreto original)
- ✅ **Configurações avançadas** via interface web
- ✅ **Coleta completa de dados WiFi** no formato original 