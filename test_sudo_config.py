#!/usr/bin/env python3

import paramiko
import os

# Configurações SSH
SSH_HOST = '192.168.68.106'
SSH_USER = 'eduardo-wanderley'
SSH_KEY = '/home/eduardo-wanderley/.ssh/id_rsa'
REMOTE_PATH = '/home/eduardo-wanderley/Desktop/dsl-mininet'

def test_sudo_config():
    print("Testando configuração do sudo na VM...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, key_filename=SSH_KEY)
        print("✓ Conexão SSH estabelecida")
        
        # Testar se o script de configuração existe
        stdin, stdout, stderr = ssh.exec_command(f"ls -la {REMOTE_PATH}/configurar_sudo.sh")
        if "configurar_sudo.sh" in stdout.read().decode():
            print("✓ Script de configuração encontrado")
        else:
            print("✗ Script de configuração não encontrado")
            return False
        
        # Testar se o usuário pode executar sudo sem senha
        stdin, stdout, stderr = ssh.exec_command("sudo -n whoami")
        saida = stdout.read().decode().strip()
        erro = stderr.read().decode().strip()
        
        if saida == "root":
            print("✓ Usuário pode executar sudo sem senha")
            return True
        else:
            print(f"✗ Sudo ainda precisa de senha: {erro}")
            print("Executando configuração automática...")
            
            # Executar configuração automática
            stdin, stdout, stderr = ssh.exec_command(f"sudo {REMOTE_PATH}/configurar_sudo.sh")
            setup_saida = stdout.read().decode() + stderr.read().decode()
            print(f"Setup: {setup_saida}")
            
            # Testar novamente
            stdin, stdout, stderr = ssh.exec_command("sudo -n whoami")
            saida = stdout.read().decode().strip()
            
            if saida == "root":
                print("✓ Configuração automática funcionou!")
                return True
            else:
                print("✗ Configuração automática falhou")
                return False
            
    except Exception as e:
        print(f"✗ Erro na conexão SSH: {e}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    test_sudo_config() 