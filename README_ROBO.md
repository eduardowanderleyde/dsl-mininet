# 🤖 Integração com Robô Real - DSL Mininet-WiFi v4.0

## 🎯 Visão Geral

O sistema agora suporta **execução em robôs físicos** além da simulação virtual! Você pode:

1. **Planejar** o cenário na interface web
2. **Simular** no Mininet-WiFi para validar
3. **Executar** no robô real para dados físicos

## 🚀 Como Funciona

### 📋 Fluxo Completo

```
Interface Web → Cenário JSON → Script Python → Robô Real → Dados WiFi Reais
```

### 🔧 Componentes

- **Interface Web**: Configuração e controle
- **Script Gerador**: Cria código Python para o robô
- **Comunicação**: USB/Serial ou SSH
- **Robô**: Executa movimento e coleta dados
- **Logs**: Dados reais salvos em CSV

## 🤖 Configuração do Robô

### Opção 1: Arduino + WiFi Shield

1. **Hardware necessário**:
   - Arduino Uno/Mega
   - WiFi Shield ou ESP8266
   - Motores DC + Driver L298N
   - Chassis de robô

2. **Upload do código**:
   ```bash
   # Carregue o arquivo exemplo_robo_arduino.ino no Arduino
   # Conecte via USB ao computador
   ```

3. **Comandos suportados**:
   - `TEST` - Teste de conexão
   - `MOVE x y` - Move para posição (x,y)
   - `STOP` - Para o robô
   - `STATUS` - Mostra posição atual

### Opção 2: Raspberry Pi + WiFi

1. **Hardware necessário**:
   - Raspberry Pi 3/4
   - Módulo WiFi integrado
   - Motores + Driver
   - Chassis de robô

2. **Instalação**:
   ```bash
   # No Raspberry Pi
   sudo apt update
   sudo apt install python3-pip
   pip3 install pyserial
   ```

3. **Script Python** (gerado automaticamente pelo sistema)

## 🔌 Conexão com o Sistema

### Método 1: USB/Serial (Recomendado)

1. **Conecte o robô via USB**
2. **Acesse a interface web**: http://localhost:5000
3. **Clique em "Executar no Robô"** no cenário desejado
4. **O sistema detecta automaticamente** a porta USB

### Método 2: SSH (Raspberry Pi)

1. **Configure IP do Raspberry Pi** no sistema
2. **Conecte via rede WiFi**
3. **O sistema envia script via SSH**

### Método 3: Manual

1. **Gere o script** na interface web
2. **Copie manualmente** para o robô
3. **Execute**: `python3 robo_script_*.py`

## 📊 Dados Coletados

O robô coleta **dados WiFi reais**:

- **📶 RSSI**: Força do sinal em dBm
- **⏱️ Latência**: Tempo de resposta da rede
- **📡 SSID**: Rede WiFi conectada
- **🔄 Handover**: Detecção de troca de AP
- **📍 Posição**: Coordenadas (x,y) do robô

### Exemplo de Log

```csv
timestamp,x,y,rssi,latency,ssid,handover
2024-01-15 10:30:15,15.0,20.0,-45,2.5,meshNet,False
2024-01-15 10:30:16,16.0,20.0,-47,2.8,meshNet,False
2024-01-15 10:30:17,25.0,20.0,-65,5.2,meshNet,True
```

## ⚙️ Configurações

### No Sistema (Interface Web)

- **Velocidade de Movimento**: 0.1-10 m/s
- **Intervalo de Amostragem**: 0.1-5 segundos
- **Modelo de Propagação**: Simples/Log-Distance/Friis/etc.
- **Tipo de Mobilidade**: Discreta/Contínua/Random Walk

### No Robô (Arduino)

```cpp
const int VELOCIDADE_PADRAO = 150;  // 0-255
const int TEMPO_MOVIMENTO = 1000;   // ms
```

## 🛠️ Troubleshooting

### Robô não é detectado

1. **Verifique conexão USB**
2. **Teste com Arduino IDE** (Monitor Serial)
3. **Verifique baudrate** (9600)
4. **Reinicie o robô**

### Movimento incorreto

1. **Ajuste pinos dos motores** no código Arduino
2. **Calibre velocidade** e tempo de movimento
3. **Verifique direção** dos motores

### Dados WiFi não coletados

1. **Verifique interface WiFi** no robô
2. **Teste comandos**: `iw dev wlan0 link`
3. **Verifique permissões** (sudo se necessário)

## 📋 Exemplo de Uso

### 1. Criar Cenário

```json
{
  "ssid": "meshNet",
  "aps": [
    {"name": "ap1", "x": 10, "y": 20, "range": 25},
    {"name": "ap2", "x": 30, "y": 20, "range": 25}
  ],
  "stations": [
    {
      "name": "robo1",
      "start_x": 5, "start_y": 20,
      "trajectory": [[15,20], [25,20], [35,20]]
    }
  ],
  "propagation": {
    "mobility_type": "continuous",
    "mobility_speed": 2.0,
    "sampling_interval": 0.5
  }
}
```

### 2. Executar

1. **Acesse**: http://localhost:5000
2. **Clique**: "Executar no Robô"
3. **Conecte robô** via USB
4. **Aguarde** execução automática

### 3. Resultados

- **Logs salvos** em `results/robo_log_*.csv`
- **Dados em tempo real** na interface
- **Gráficos** de RSSI vs posição

## 🎯 Benefícios

- **✅ Dados Reais**: Coleta de dados WiFi físicos
- **✅ Validação**: Confirma simulações com dados reais
- **✅ Flexibilidade**: Funciona com diferentes robôs
- **✅ Simplicidade**: Interface web intuitiva
- **✅ Compatibilidade**: Arduino, Raspberry Pi, etc.

## 🔮 Próximos Passos

- [ ] **Calibração automática** de movimento
- [ ] **Mapas de calor** em tempo real
- [ ] **Múltiplos robôs** simultâneos
- [ ] **Integração ROS** (Robot Operating System)
- [ ] **Interface móvel** para controle remoto

---

**🎉 Agora você tem um sistema completo: Simulação + Robô Real!** 