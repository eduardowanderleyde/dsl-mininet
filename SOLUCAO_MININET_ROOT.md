# Solução para Mininet Precisa Rodar como Root

## Problema
O Mininet-WiFi precisa de privilégios de root para funcionar, mas o usuário `eduardo-wanderley` na VM precisa de senha para executar `sudo`.

## Soluções Disponíveis

### 1. Configurar Sudo Sem Senha (Recomendado)

**Na VM, execute como root:**
```bash
# Conectar como root na VM
ssh root@192.168.68.106

# Ou usar sudo se tiver acesso
sudo visudo

# Adicionar esta linha no final do arquivo:
eduardo-wanderley ALL=(ALL) NOPASSWD:ALL

# Salvar e sair
```

**Testar:**
```bash
# Conectar como eduardo-wanderley
ssh eduardo-wanderley@192.168.68.106

# Testar sudo sem senha
sudo -n whoami
# Deve retornar: root
```

### 2. Usar o Script Automático

O sistema tenta configurar automaticamente, mas pode falhar se o usuário não tiver permissões para modificar `/etc/sudoers`.

### 3. Configurar PolicyKit (Alternativa)

Se não conseguir configurar sudo, use `pkexec`:

```bash
# Na VM, instalar policykit
sudo apt-get install policykit-1

# Criar arquivo de política
sudo nano /etc/polkit-1/localauthority/50-local.d/10-mininet.pkla
```

**Conteúdo:**
```
[Allow eduardo-wanderley to run mininet]
Identity=unix-user:eduardo-wanderley
Action=org.freedesktop.policykit.exec
ResultAny=yes
```

### 4. Executar Mininet Diretamente como Root

**Opção mais simples:**
```bash
# Na VM, conectar como root
ssh root@192.168.68.106

# Navegar para o diretório
cd /home/eduardo-wanderley/Desktop/dsl-mininet

# Executar diretamente
python3 executa_cenario.py cenario_teste.json
```

## Status Atual

O sistema agora tenta múltiplos métodos:
1. **sudo** (pode falhar se precisar de senha)
2. **pkexec** (pode falhar se não configurado)
3. **usuário normal** (vai falhar mas mostrar erro claro)

## Próximos Passos

1. **Configure o sudo sem senha** na VM (método mais simples)
2. **Teste na interface web** executando um cenário
3. **Se funcionar**, o sistema estará pronto para uso

## Verificação

Após configurar, acesse `http://localhost:5000` e execute um cenário. O sistema deve funcionar sem pedir senha. 