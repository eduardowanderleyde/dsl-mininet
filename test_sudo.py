#!/usr/bin/env python3

import paramiko
import os

# Configurações SSH
SSH_HOST = '192.168.68.106'
SSH_USER = 'eduardo-wanderley'
SSH_KEY = '/home/eduardo-wanderley/.ssh/id_rsa'

def test_sudo():
    print("Testando permissões sudo na VM...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, key_filename=SSH_KEY)
        print("✓ Conexão SSH estabelecida")
        
        # Testar se o usuário pode executar sudo sem senha
        stdin, stdout, stderr = ssh.exec_command("sudo -n whoami")
        saida = stdout.read().decode().strip()
        erro = stderr.read().decode().strip()
        
        if saida == "root":
            print("✓ Usuário pode executar sudo sem senha")
            return True
        elif erro and "password" in erro.lower():
            print("✗ Usuário precisa de senha para sudo")
            return False
        else:
            print(f"✗ Erro desconhecido: {erro}")
            return False
            
    except Exception as e:
        print(f"✗ Erro na conexão SSH: {e}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    test_sudo() 