# Resumo Executivo - Descobertas Mininet-WiFi

## 🎯 Problema Principal
O cenário original do "quarto" com 3 APs triangulares não funcionava - station não conectava a nenhum AP.

## 🔍 Causa Raiz Encontrada
**Nomes de stations com underscores causam falhas no Mininet-WiFi**

### ❌ Nomes que NÃO funcionam:
- `raspberry_pi`
- `raspberrypi` 
- `mobile_sta`

### ✅ Nomes que funcionam:
- `sta1`
- `sta2`
- `sta3`

## 📊 Resultados dos Testes

| Cenário | APs | Nome Station | Resultado |
|---------|-----|--------------|-----------|
| Mínimo | 1 | sta1 | ✅ Funcionou |
| 2 APs | 2 | sta1 | ✅ Funcionou |
| 3 APs Linha | 3 | sta1 | ✅ Funcionou |
| 3 APs Triangulares | 3 | sta1 | ✅ Funcionou |
| 3 APs Triangulares | 3 | raspberry_pi | ❌ Falhou |

## 🚀 Soluções Implementadas

### 1. Cenários Funcionais Criados:
- `cenarios_novos/cenario_2aps_baseado_minimo.json` ✅
- `cenarios_novos/cenario_3aps_linha.json` ✅  
- `cenarios_novos/cenario_quarto_funcional.json` ✅

### 2. Script Modificado:
- Adicionado suporte a parâmetros `range` e `txpower`
- Melhor tratamento de erros

## ⚠️ Limitações Descobertas

### Handover Automático
- **Mininet-WiFi NÃO faz handover automático**
- Station permanece conectada ao primeiro AP
- Scan detecta múltiplos APs, mas não muda conexão

### Configuração de Range
- Parâmetros `range` e `txpower` são complexos
- Não garantem conectividade mesmo quando corretos
- Melhor usar configurações padrão

## 💡 Recomendações

### Para Usar Agora:
1. **Use nomes simples**: `sta1`, `sta2`, etc.
2. **Evite underscores**: Não use `raspberry_pi`
3. **Teste com cenários simples primeiro**
4. **Sempre limpe ambiente**: `sudo mn -c`

### Para Implementar Handover:
1. Criar script que força desconexão/reconexão
2. Monitorar RSSI e forçar mudança manualmente
3. Implementar lógica de handover customizada

## 📁 Arquivos Funcionais
```
cenarios_novos/
├── cenario_2aps_baseado_minimo.json ✅
├── cenario_3aps_linha.json ✅
└── cenario_quarto_funcional.json ✅
```

## 🎯 Conclusão
O problema era simples: **nomes de stations com underscores não funcionam no Mininet-WiFi**. Com nomes simples como `sta1`, todos os cenários funcionam perfeitamente, incluindo o cenário do quarto com 3 APs triangulares. 