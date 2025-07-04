#!/usr/bin/env python3
"""
Sistema de logs automáticos detalhados para DSL Mininet-WiFi v4.0
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json

class RoboLogger:
    """Sistema de logs para execução de robôs"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.setup_logging()
        
    def setup_logging(self):
        """Configura o sistema de logs"""
        # Criar diretório de logs se não existir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Logger principal
        self.logger = logging.getLogger('robo_system')
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicação de handlers
        if not self.logger.handlers:
            # Handler para arquivo com rotação
            file_handler = RotatingFileHandler(
                f'{self.log_dir}/robo_system.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formato dos logs
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_execucao_robo(self, cenario, status, detalhes=""):
        """Log específico para execução de robô"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "cenario": cenario,
            "status": status,
            "detalhes": detalhes,
            "tipo": "execucao_robo"
        }
        
        # Salvar em arquivo JSON para fácil parsing
        log_file = f'{self.log_dir}/execucoes_robo.json'
        logs = []
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        # Log no sistema principal
        self.logger.info(f"ROBÔ: {cenario} - {status} - {detalhes}")
    
    def log_conexao_ssh(self, ip, status, detalhes=""):
        """Log específico para tentativas de conexão SSH"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "ip": ip,
            "status": status,
            "detalhes": detalhes,
            "tipo": "conexao_ssh"
        }
        
        log_file = f'{self.log_dir}/conexoes_ssh.json'
        logs = []
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        self.logger.info(f"SSH: {ip} - {status} - {detalhes}")
    
    def log_dados_wifi(self, dados):
        """Log para dados WiFi coletados"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "dados": dados,
            "tipo": "dados_wifi"
        }
        
        log_file = f'{self.log_dir}/dados_wifi.json'
        logs = []
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        self.logger.debug(f"WiFi: RSSI={dados.get('rssi')}, SSID={dados.get('ssid')}")
    
    def get_logs_recentes(self, tipo=None, limit=50):
        """Retorna logs recentes"""
        logs = []
        
        if tipo == "execucao_robo":
            log_file = f'{self.log_dir}/execucoes_robo.json'
        elif tipo == "conexao_ssh":
            log_file = f'{self.log_dir}/conexoes_ssh.json'
        elif tipo == "dados_wifi":
            log_file = f'{self.log_dir}/dados_wifi.json'
        else:
            # Retorna todos os tipos
            all_logs = []
            for log_type in ["execucoes_robo.json", "conexoes_ssh.json", "dados_wifi.json"]:
                log_file = f'{self.log_dir}/{log_type}'
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r') as f:
                            all_logs.extend(json.load(f))
                    except:
                        pass
            
            # Ordenar por timestamp e retornar os mais recentes
            all_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return all_logs[:limit]
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                return logs[:limit]
            except:
                pass
        
        return logs

# Instância global do logger
robo_logger = RoboLogger() 