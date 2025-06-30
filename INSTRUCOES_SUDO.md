# Instruções para Configurar Sudo Sem Senha na VM

## Problema
O Mininet-WiFi precisa rodar como root, mas o usuário `eduardo-wanderley` na VM precisa de senha para executar `sudo`.

## Solução Automática
O sistema tenta configurar automaticamente o sudo sem senha, mas pode falhar se o usuário não tiver permissões para modificar o `/etc/sudoers`.

## Solução Manual (se necessário)

### 1. Conectar na VM como root ou com sudo
```bash
# Via SSH (se tiver acesso root)
ssh root@192.168.68.106

# Ou via console da VM
```

### 2. Configurar sudo sem senha
```bash
# Editar o arquivo sudoers
sudo visudo

# Adicionar esta linha no final do arquivo:
eduardo-wanderley ALL=(ALL) NOPASSWD:ALL

# Salvar e sair (Ctrl+X, Y, Enter no nano)
```

### 3. Testar a configuração
```bash
# Conectar como eduardo-wanderley
ssh eduardo-wanderley@192.168.68.106

# Testar sudo sem senha
sudo -n whoami
# Deve retornar: root
```

### 4. Alternativa: Usar pkexec
Se não conseguir configurar o sudo, pode usar `pkexec`:

```bash
# Na VM, instalar policykit
sudo apt-get install policykit-1

# Criar arquivo de política
sudo nano /etc/polkit-1/localauthority/50-local.d/10-mininet.pkla
```

Conteúdo do arquivo:
```
[Allow eduardo-wanderley to run mininet]
Identity=unix-user:eduardo-wanderley
Action=org.freedesktop.policykit.exec
ResultAny=yes
```

### 5. Testar execução
```bash
# Testar com pkexec
pkexec python3 executa_cenario.py cenario_teste.json
```

## Verificação
Após configurar, teste na interface web executando um cenário. O sistema deve funcionar sem pedir senha. 