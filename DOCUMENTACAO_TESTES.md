# Documentação dos Testes - DSL Mininet-WiFi

## Resumo dos Problemas Encontrados

Durante os testes com diferentes cenários, identificamos vários problemas e limitações do Mininet-WiFi que afetam a simulação de handover e conectividade.

## 1. Problema Principal: Conectividade com Múltiplos APs

### Cenário Original (Quarto)
- **Configuração**: 3 APs em posições triangulares
- **Problema**: Station não conectava a nenhum AP
- **Sintomas**: RSSI -100, latência 9999, scan não detectava APs

### Investigação Realizada

#### Teste 1: Cenário Mínimo (Funcionou)
```json
{
  "aps": [{"name": "ap1", "x": 10.0, "y": 10.0}],
  "stations": [{"name": "sta1", "start_x": 10.0, "start_y": 10.0}]
}
```
**Resultado**: ✅ Funcionou perfeitamente
- RSSI: -36
- Latência: ~0.03ms
- Scan: Detectou AP corretamente

#### Teste 2: 2 APs Próximos com Range (Falhou)
```json
{
  "aps": [
    {"name": "ap1", "x": 10.0, "y": 10.0, "range": 30},
    {"name": "ap2", "x": 20.0, "y": 10.0, "range": 30}
  ]
}
```
**Resultado**: ❌ Não conectou
- Mininet-WiFi sugeriu range mínimo de 116m

#### Teste 3: 2 APs com Range 120m e TxPower (Falhou)
```json
{
  "aps": [
    {"name": "ap1", "x": 10.0, "y": 10.0, "range": 120, "txpower": 3},
    {"name": "ap2", "x": 20.0, "y": 10.0, "range": 120, "txpower": 3}
  ]
}
```
**Resultado**: ❌ Ainda não conectou
- Mesmo com configurações otimizadas

#### Teste 4: 2 APs Baseado no Mínimo (Funcionou)
```json
{
  "aps": [
    {"name": "ap1", "x": 10.0, "y": 10.0},
    {"name": "ap2", "x": 20.0, "y": 10.0}
  ],
  "stations": [{"name": "sta1", "start_x": 10.0, "start_y": 10.0}]
}
```
**Resultado**: ✅ Funcionou
- Detectou ambos os APs: `Scan=meshNet:-36;meshNet:-36`
- Conectou ao ap1 e manteve conexão

#### Teste 5: 3 APs em Linha (Funcionou)
```json
{
  "aps": [
    {"name": "ap1", "x": 10.0, "y": 10.0},
    {"name": "ap2", "x": 20.0, "y": 10.0},
    {"name": "ap3", "x": 30.0, "y": 10.0}
  ],
  "stations": [{"name": "sta1", "start_x": 15.0, "start_y": 10.0}]
}
```
**Resultado**: ✅ Funcionou
- Detectou todos os 3 APs: `Scan=meshNet:-36;meshNet:-36;meshNet:-36`
- Conectou ao ap1 e manteve conexão

#### Teste 6: 3 APs Triangulares com sta1 (Funcionou)
```json
{
  "aps": [
    {"name": "ap1", "x": 10.0, "y": 10.0},
    {"name": "ap2", "x": 20.0, "y": 10.0},
    {"name": "ap3", "x": 15.0, "y": 20.0}
  ],
  "stations": [{"name": "sta1", "start_x": 15.0, "start_y": 15.0}]
}
```
**Resultado**: ✅ Funcionou
- Detectou todos os 3 APs
- Conectou ao ap1 e manteve conexão

#### Teste 7: 3 APs Triangulares com raspberry_pi (Falhou)
```json
{
  "stations": [{"name": "raspberry_pi", "start_x": 15.0, "start_y": 15.0}]
}
```
**Resultado**: ❌ Não conectou
- Mesma configuração, apenas nome diferente

## 2. Descobertas Importantes

### A. Limitação de Nomes de Stations
- **Problema**: Nomes como "raspberry_pi", "raspberrypi", "mobile_sta" causam falhas
- **Solução**: Usar nomes simples como "sta1", "sta2", etc.
- **Possível Causa**: Conflito com nomes reservados ou caracteres especiais

### B. Parâmetros Range e TxPower
- **Range**: Mininet-WiFi requer mínimo de 116m para funcionar
- **TxPower**: Deve ser 3dBm para range de 120m
- **Problema**: Mesmo com configurações corretas, não garante conectividade

### C. Posicionamento dos APs
- **APs em Linha**: Funciona bem
- **APs Triangulares**: Funciona apenas com nomes específicos de stations
- **Distância**: APs muito próximos (< 10 unidades) podem causar interferência

### D. Comportamento de Handover
- **Realidade**: Mininet-WiFi NÃO força handover automaticamente
- **Station**: Mantém conexão com o primeiro AP que conectou
- **Scan**: Detecta múltiplos APs, mas não muda de conexão

## 3. Cenários Funcionais Criados

### Cenário 1: 2 APs Baseado no Mínimo
- **Arquivo**: `cenarios_novos/cenario_2aps_baseado_minimo.json`
- **Status**: ✅ Funcional
- **Uso**: Teste básico de conectividade com 2 APs

### Cenário 2: 3 APs em Linha
- **Arquivo**: `cenarios_novos/cenario_3aps_linha.json`
- **Status**: ✅ Funcional
- **Uso**: Teste de detecção de múltiplos APs

### Cenário 3: 3 APs Triangulares (Quarto)
- **Arquivo**: `cenarios_novos/cenario_quarto_funcional.json`
- **Status**: ✅ Funcional (apenas com nome "sta1")
- **Uso**: Simulação de ambiente de quarto

## 4. Limitações Identificadas

### A. Handover Automático
- Mininet-WiFi não implementa handover automático
- Station permanece conectada ao primeiro AP
- Necessário implementar lógica manual de handover

### B. Nomes de Stations
- Restrições severas em nomes de stations
- Nomes com underscores ou palavras específicas causam falhas
- Necessário usar nomes simples e curtos

### C. Configuração de Range
- Parâmetros range e txpower são complexos
- Não garantem conectividade mesmo quando configurados corretamente
- Melhor usar configurações padrão do Mininet-WiFi

## 5. Recomendações

### Para Cenários Funcionais:
1. Usar nomes simples para stations: "sta1", "sta2", etc.
2. Evitar parâmetros range e txpower complexos
3. Posicionar APs em linha ou com distância adequada
4. Testar sempre com cenário mínimo primeiro

### Para Implementar Handover:
1. Implementar lógica manual de desconexão/reconexão
2. Monitorar RSSI e forçar mudança quando necessário
3. Usar scripts adicionais para simular movimento real

### Para Debugging:
1. Sempre limpar ambiente com `sudo mn -c`
2. Verificar logs detalhados de conectividade
3. Testar com cenários simples antes de complexos

## 6. Próximos Passos

1. **Implementar Handover Manual**: Criar script que força desconexão/reconexão
2. **Otimizar Nomes**: Encontrar padrão de nomes que funcionam consistentemente
3. **Testar Cenários Reais**: Aplicar descobertas em cenários mais complexos
4. **Documentar Soluções**: Criar guia de troubleshooting para problemas futuros 