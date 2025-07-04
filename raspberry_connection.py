#!/usr/bin/env python3
"""
Sistema de conexão persistente com Raspberry Pi
"""

import paramiko
import threading
import time
import json
import os
from datetime import datetime
from logger_config import robo_logger

class RaspberryConnection:
    """Gerenciador de conexão persistente com Raspberry Pi"""
    
    def __init__(self, ip="192.168.68.107", username="eduardowanderley", password="200982"):
        self.ip = ip
        self.username = username
        self.password = password
        self.ssh_client = None
        self.sftp_client = None
        self.connected = False
        self.connection_lock = threading.Lock()
        self.keep_alive_thread = None
        self.running = True
        
        # Configurações de reconexão
        self.reconnect_interval = 30  # segundos
        self.max_reconnect_attempts = 5
        
        # Iniciar thread de keep-alive
        self.start_keep_alive()
    
    def connect(self):
        """Estabelece conexão SSH com o Raspberry Pi"""
        try:
            with self.connection_lock:
                if self.connected and self.ssh_client:
                    return True
                
                robo_logger.log_conexao_ssh(self.ip, "tentando", "Estabelecendo conexão SSH...")
                
                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Tentar conectar com timeout
                self.ssh_client.connect(
                    self.ip,
                    username=self.username,
                    password=self.password,
                    timeout=10,
                    banner_timeout=60
                )
                
                # Testar conexão
                stdin, stdout, stderr = self.ssh_client.exec_command("echo 'Conexão SSH ativa'", timeout=5)
                if stdout.channel.recv_exit_status() == 0:
                    self.connected = True
                    self.sftp_client = self.ssh_client.open_sftp()
                    
                    robo_logger.log_conexao_ssh(self.ip, "conectado", "Conexão SSH estabelecida com sucesso")
                    print(f"✅ Conectado no Raspberry Pi: {self.ip}")
                    return True
                else:
                    raise Exception("Teste de conexão falhou")
                    
        except Exception as e:
            self.connected = False
            self.ssh_client = None
            self.sftp_client = None
            
            robo_logger.log_conexao_ssh(self.ip, "falhou", f"Erro na conexão: {str(e)}")
            print(f"❌ Falha na conexão SSH: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do Raspberry Pi"""
        with self.connection_lock:
            self.connected = False
            self.running = False
            
            if self.sftp_client:
                try:
                    self.sftp_client.close()
                except:
                    pass
                self.sftp_client = None
            
            if self.ssh_client:
                try:
                    self.ssh_client.close()
                except:
                    pass
                self.ssh_client = None
            
            robo_logger.log_conexao_ssh(self.ip, "desconectado", "Conexão SSH fechada")
            print(f"🔌 Desconectado do Raspberry Pi: {self.ip}")
    
    def is_connected(self):
        """Verifica se está conectado"""
        if not self.connected or not self.ssh_client:
            return False
        
        try:
            # Teste rápido de conexão
            stdin, stdout, stderr = self.ssh_client.exec_command("echo 'ping'", timeout=3)
            return stdout.channel.recv_exit_status() == 0
        except:
            self.connected = False
            return False
    
    def ensure_connection(self):
        """Garante que a conexão está ativa, reconectando se necessário"""
        if self.is_connected():
            return True
        
        print(f"🔄 Reconectando no Raspberry Pi: {self.ip}")
        return self.connect()
    
    def execute_command(self, command, timeout=30):
        """Executa comando no Raspberry Pi"""
        if not self.ensure_connection():
            raise Exception("Não foi possível estabelecer conexão")
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            exit_status = stdout.channel.recv_exit_status()
            
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            return {
                'success': exit_status == 0,
                'output': output,
                'error': error,
                'exit_status': exit_status
            }
            
        except Exception as e:
            robo_logger.log_conexao_ssh(self.ip, "erro_comando", f"Erro ao executar comando: {str(e)}")
            raise e
    
    def upload_file(self, local_path, remote_path):
        """Envia arquivo para o Raspberry Pi"""
        if not self.ensure_connection():
            raise Exception("Não foi possível estabelecer conexão")
        
        try:
            self.sftp_client.put(local_path, remote_path)
            robo_logger.log_conexao_ssh(self.ip, "upload_sucesso", f"Arquivo enviado: {local_path} -> {remote_path}")
            return True
        except Exception as e:
            robo_logger.log_conexao_ssh(self.ip, "upload_falhou", f"Erro ao enviar arquivo: {str(e)}")
            raise e
    
    def download_file(self, remote_path, local_path):
        """Baixa arquivo do Raspberry Pi"""
        if not self.ensure_connection():
            raise Exception("Não foi possível estabelecer conexão")
        
        try:
            self.sftp_client.get(remote_path, local_path)
            robo_logger.log_conexao_ssh(self.ip, "download_sucesso", f"Arquivo baixado: {remote_path} -> {local_path}")
            return True
        except Exception as e:
            robo_logger.log_conexao_ssh(self.ip, "download_falhou", f"Erro ao baixar arquivo: {str(e)}")
            raise e
    
    def get_wifi_info(self):
        """Obtém informações WiFi do Raspberry Pi"""
        if not self.ensure_connection():
            return None
        
        try:
            # Comando para obter informações WiFi
            wifi_cmd = """
            echo "=== WiFi Info ==="
            iw dev wlan0 link
            echo "=== IP Info ==="
            ip addr show wlan0
            echo "=== Signal Strength ==="
            iw dev wlan0 link | grep signal
            """
            
            result = self.execute_command(wifi_cmd)
            if result['success']:
                return result['output']
            else:
                return f"Erro: {result['error']}"
                
        except Exception as e:
            return f"Erro ao obter info WiFi: {str(e)}"
    
    def start_keep_alive(self):
        """Inicia thread de keep-alive para manter conexão ativa"""
        def keep_alive_loop():
            while self.running:
                try:
                    if self.connected:
                        # Teste de conexão a cada 60 segundos
                        if not self.is_connected():
                            print(f"🔄 Conexão perdida, tentando reconectar...")
                            self.connect()
                        else:
                            # Comando de keep-alive
                            self.execute_command("echo 'keep-alive'", timeout=5)
                    
                    time.sleep(60)  # Verificar a cada minuto
                    
                except Exception as e:
                    print(f"Erro no keep-alive: {e}")
                    time.sleep(30)
        
        self.keep_alive_thread = threading.Thread(target=keep_alive_loop, daemon=True)
        self.keep_alive_thread.start()
    
    def get_status(self):
        """Retorna status da conexão"""
        return {
            'connected': self.is_connected(),
            'ip': self.ip,
            'username': self.username,
            'last_check': datetime.now().isoformat()
        }

# Instância global da conexão
raspberry_conn = RaspberryConnection() 