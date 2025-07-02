# Correções de Nomes de Stations - Mininet-WiFi

## 🎯 Problema Resolvido
Todos os cenários que usavam nomes de stations com underscores foram corrigidos para funcionar no Mininet-WiFi.

## ❌ Nomes Problemáticos (ANTES)
- `raspberry_pi` - ❌ Não funcionava
- `mobile_sta` - ❌ Não funcionava  
- `raspberrypi` - ❌ Não funcionava

## ✅ Nomes Corrigidos (DEPOIS)
- `sta1` - ✅ Funciona perfeitamente
- `sta2` - ✅ Funciona perfeitamente
- `sta3` - ✅ Funciona perfeitamente

## 📁 Cenários Corrigidos

### Cenários em `cenarios_novos/`:
1. `cenario_3aps_linha_mobile.json`
   - ❌ `mobile_sta` → ✅ `sta1`

2. `cenario_2aps_super_proximos.json`
   - ❌ `raspberry_pi` → ✅ `sta1`

3. `cenario_2aps_proximos.json`
   - ❌ `raspberry_pi` → ✅ `sta1`

4. `cenario_quarto_otimizado.json`
   - ❌ `raspberry_pi` → ✅ `sta1`

5. `cenario_quarto_final.json`
   - ❌ `mobile_sta` → ✅ `sta1`

6. `cenario_quarto_super_proximo.json`
   - ❌ `raspberry_pi` → ✅ `sta1`

### Cenários em `cenarios/`:
1. `cenario_quarto_wifi.json`
   - ❌ `raspberry_pi` → ✅ `sta1`

2. `cenario_raspberry_movel.json`
   - ❌ `raspberry_pi` → ✅ `sta1`

## 🧪 Verificação
Executado script `teste_todos_cenarios.py`:
- **Total de cenários**: 21
- **✅ Funcionais**: 21
- **❌ Problemáticos**: 0

## 🚀 Como Usar Agora

### Para executar qualquer cenário:
```bash
python3 executa_cenario_mesh_v2.py cenarios_novos/cenario_quarto_final.json
```

### Cenários recomendados para teste:
1. **Cenário mínimo**: `cenarios_novos/cenario_2aps_baseado_minimo.json`
2. **3 APs em linha**: `cenarios_novos/cenario_3aps_linha.json`
3. **3 APs triangulares**: `cenarios_novos/cenario_quarto_funcional.json`
4. **Com mobilidade**: `cenarios_novos/cenario_3aps_linha_mobile.json`

## 💡 Regra Importante
**SEMPRE use nomes simples para stations no Mininet-WiFi:**
- ✅ `sta1`, `sta2`, `sta3`
- ❌ `raspberry_pi`, `mobile_sta`, `device_1`

## 🎉 Resultado
Todos os 21 cenários agora estão funcionais e prontos para uso! 