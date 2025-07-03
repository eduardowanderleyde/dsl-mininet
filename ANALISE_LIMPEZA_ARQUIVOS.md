# 🧹 Análise de Limpeza de Arquivos - DSL Mininet-WiFi v4.0

## 📊 Status Atual: MUITOS ARQUIVOS DESNECESSÁRIOS

### ✅ ARQUIVOS ESSENCIAIS (MANTER)

#### 🚀 **Scripts Principais**
- `executa_cenario_mesh_v4.py` - **SCRIPT PRINCIPAL v4.0**
- `app.py` - **Interface web Flask**

#### 📁 **Estrutura de Pastas**
- `cenarios/` - Cenários JSON ativos
- `results/` - Logs CSV da simulação
- `templates/` - Templates HTML da interface web
- `venv/` - Ambiente virtual Python

#### 📋 **Configuração e Documentação**
- `requirements.txt` - Dependências Python
- `README.md` - Documentação principal
- `ESTADO_ATUAL_V4.md` - Status atual do projeto

### 🗑️ ARQUIVOS PARA REMOÇÃO IMEDIATA

#### 📜 **Scripts Antigos (Funcionalidade Integrada na v4.0)**
- `executa_cenario_mesh_v2.py` - ❌ Versão antiga
- `executa_cenario_mesh_v3.py` - ❌ Versão antiga
- `executa_cenario_scan_wifi.py` - ❌ Funcionalidade integrada
- `executa_raspberry_movel.py` - ❌ Funcionalidade integrada
- `executa_cenario_handover_forcado.py` - ❌ Funcionalidade integrada
- `executa_cenario_mesh.py` - ❌ Versão antiga
- `executa_cenario.py` - ❌ Versão antiga

#### 🧪 **Scripts de Teste (Não Mais Necessários)**
- `teste_novas_ferramentas.py` - ❌ Teste antigo
- `teste_todos_cenarios.py` - ❌ Teste antigo
- `teste_limites_conectividade.py` - ❌ Teste antigo
- `teste_manual_incremental.py` - ❌ Teste antigo
- `teste_cenarios.py` - ❌ Teste antigo

#### 📊 **Scripts de Análise (Funcionalidade Integrada)**
- `analisador_performance_avancado.py` - ❌ Funcionalidade integrada
- `analisar_raspberry_pi.py` - ❌ Funcionalidade integrada
- `analisar_mesh.py` - ❌ Funcionalidade integrada
- `analisar_logs.py` - ❌ Funcionalidade integrada
- `gerador_relatorios.py` - ❌ Funcionalidade integrada

#### 📄 **Documentação Antiga (Redundante)**
- `SUGESTOES_MELHORIAS_FERRAMENTAS.md` - ❌ Documentação antiga
- `ESTADO_ATUAL_CENARIOS.md` - ❌ Documentação antiga
- `MELHORIAS_IMPLEMENTADAS_V3.md` - ❌ Documentação antiga
- `ANALISE_FUNCOES_MELHORIAS.md` - ❌ Documentação antiga
- `CORRECOES_NOMES_STATIONS.md` - ❌ Documentação antiga
- `RESUMO_DESCOBERTAS.md` - ❌ Documentação antiga
- `DOCUMENTACAO_TESTES.md` - ❌ Documentação antiga
- `RELATORIO_LIMITES_CONECTIVIDADE.md` - ❌ Documentação antiga
- `IMPLEMENTACAO_MESH_MONITORING.md` - ❌ Documentação antiga
- `DOCUMENTACAO_COMPLETA.md` - ❌ Documentação antiga

#### 📁 **Arquivos Temporários e Antigos**
- `1.txt` - ❌ Arquivo temporário
- `station1_log.csv` - ❌ Log antigo
- `cenario_exemplo_3.json` - ❌ Cenário antigo (duplicado)
- `cenario_meshNet_1.json` - ❌ Cenário antigo (duplicado)
- `Dockerfile` - ❌ Não usado

#### 📁 **Pasta Redundante**
- `cenarios_novos/` - ❌ Cenários duplicados (mover para `cenarios/` se necessário)

### 🎯 **PLANO DE LIMPEZA**

#### **Fase 1: Remoção de Scripts Antigos**
```bash
# Remover scripts antigos
rm executa_cenario_mesh_v2.py
rm executa_cenario_mesh_v3.py
rm executa_cenario_scan_wifi.py
rm executa_raspberry_movel.py
rm executa_cenario_handover_forcado.py
rm executa_cenario_mesh.py
rm executa_cenario.py
```

#### **Fase 2: Remoção de Scripts de Teste**
```bash
# Remover scripts de teste
rm teste_*.py
```

#### **Fase 3: Remoção de Scripts de Análise**
```bash
# Remover scripts de análise
rm analisador_performance_avancado.py
rm analisar_*.py
rm gerador_relatorios.py
```

#### **Fase 4: Remoção de Documentação Antiga**
```bash
# Remover documentação antiga
rm *.md
# Manter apenas: README.md, ESTADO_ATUAL_V4.md
```

#### **Fase 5: Limpeza de Arquivos Temporários**
```bash
# Remover arquivos temporários
rm 1.txt
rm station1_log.csv
rm cenario_exemplo_3.json
rm cenario_meshNet_1.json
rm Dockerfile
```

#### **Fase 6: Organização de Cenários**
```bash
# Mover cenários úteis da pasta 'cenarios_novos' para 'cenarios'
# Remover pasta 'cenarios_novos' se vazia
```

### 📈 **RESULTADO ESPERADO APÓS LIMPEZA**

#### **Estrutura Final Limpa:**
```
dsl-mininet/
├── executa_cenario_mesh_v4.py    # Script principal v4.0
├── app.py                        # Interface web
├── requirements.txt              # Dependências
├── README.md                     # Documentação principal
├── ESTADO_ATUAL_V4.md           # Status atual
├── cenarios/                     # Cenários JSON ativos
├── results/                      # Logs CSV
├── templates/                    # Templates HTML
└── venv/                        # Ambiente virtual
```

#### **Benefícios da Limpeza:**
- ✅ **Redução de 80% dos arquivos**
- ✅ **Estrutura mais limpa e organizada**
- ✅ **Foco apenas na v4.0 funcional**
- ✅ **Manutenção mais fácil**
- ✅ **Menos confusão para novos usuários**

### 🚀 **COMANDO DE LIMPEZA AUTOMÁTICA**

O botão "🧹 Limpar Arquivos Antigos" na interface web já está configurado para remover automaticamente todos esses arquivos desnecessários. 