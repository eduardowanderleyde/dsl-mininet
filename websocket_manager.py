#!/usr/bin/env python3
"""
Sistema de WebSocket para feedback em tempo real
"""

import json
import threading
import time
from datetime import datetime
from flask_socketio import SocketIO, emit
import queue

class RealTimeManager:
    """Gerenciador de feedback em tempo real"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.active_sessions = {}
        self.message_queue = queue.Queue()
        self.running = True
        
        # Iniciar thread de processamento de mensagens
        self.message_thread = threading.Thread(target=self._process_messages, daemon=True)
        self.message_thread.start()
    
    def _process_messages(self):
        """Processa mensagens da fila e envia via WebSocket"""
        while self.running:
            try:
                message = self.message_queue.get(timeout=1)
                if message:
                    self.socketio.emit('robo_update', message)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
    
    def send_status_update(self, session_id, status, message, data=None):
        """Envia atualização de status"""
        update = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'message': message,
            'data': data or {}
        }
        
        self.message_queue.put(update)
    
    def send_ssh_log(self, session_id, ip, status, details=""):
        """Envia log de conexão SSH"""
        log = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'ssh_log',
            'ip': ip,
            'status': status,
            'details': details
        }
        
        self.message_queue.put(log)
    
    def send_wifi_data(self, session_id, dados):
        """Envia dados WiFi em tempo real"""
        data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'wifi_data',
            'dados': dados
        }
        
        self.message_queue.put(data)
    
    def send_progress(self, session_id, current, total, description=""):
        """Envia progresso da execução"""
        progress = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'progress',
            'current': current,
            'total': total,
            'percentage': int((current / total) * 100) if total > 0 else 0,
            'description': description
        }
        
        self.message_queue.put(progress)
    
    def start_session(self, session_id, cenario):
        """Inicia uma nova sessão de execução"""
        self.active_sessions[session_id] = {
            'cenario': cenario,
            'start_time': datetime.now(),
            'status': 'starting'
        }
        
        self.send_status_update(session_id, 'starting', f'Iniciando execução do cenário: {cenario}')
    
    def end_session(self, session_id, success=True):
        """Finaliza uma sessão"""
        if session_id in self.active_sessions:
            status = 'completed' if success else 'failed'
            self.active_sessions[session_id]['status'] = status
            self.active_sessions[session_id]['end_time'] = datetime.now()
            
            message = 'Execução concluída com sucesso!' if success else 'Execução falhou!'
            self.send_status_update(session_id, status, message)
    
    def get_session_info(self, session_id):
        """Retorna informações da sessão"""
        return self.active_sessions.get(session_id, {})

# Instância global (será inicializada no app.py)
realtime_manager = None 