"""Serviço de timer para reboot automático."""

import threading
import time
from typing import Callable, Optional

from src.utils.logger import Logger


class TimerService:
    """Gerencia timer para execução automática de reboots."""
    
    def __init__(self, logger: Logger, callback: Callable[[], bool]):
        """
        Inicializa o serviço de timer.
        
        Args:
            logger: Instância do logger
            callback: Função a ser chamada quando o timer disparar
        """
        self.logger = logger
        self.callback = callback
        self.is_running = False
        self.timer_thread: Optional[threading.Thread] = None
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.on_status_update: Optional[Callable[[str], None]] = None
        self.on_next_exec_update: Optional[Callable[[str], None]] = None
    
    def set_timer(self, hours: int, minutes: int, seconds: int):
        """
        Define o intervalo do timer.
        
        Args:
            hours: Horas
            minutes: Minutos
            seconds: Segundos
        """
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
    
    def get_total_seconds(self) -> int:
        """Retorna o total de segundos do timer."""
        return self.hours * 3600 + self.minutes * 60 + self.seconds
    
    def format_time(self, total_seconds: int) -> str:
        """
        Formata segundos em formato legível (HH:MM:SS).
        
        Args:
            total_seconds: Total de segundos
            
        Returns:
            String formatada
        """
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def start(self) -> bool:
        """
        Inicia o timer.
        
        Returns:
            True se iniciado com sucesso, False se timer inválido
        """
        total_seconds = self.get_total_seconds()
        
        if total_seconds <= 0:
            self.logger.warning("Tentativa de iniciar timer com valor inválido")
            return False
        
        self.logger.info(f"Timer iniciado: {self.format_time(total_seconds)} ({total_seconds} segundos)")
        self.is_running = True
        
        if self.on_status_update:
            self.on_status_update("Rodando")
        
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        
        return True
    
    def stop(self):
        """Para o timer."""
        self.logger.info("Timer parado")
        self.is_running = False
        
        if self.on_status_update:
            self.on_status_update("Parado")
        
        if self.on_next_exec_update:
            self.on_next_exec_update("--")
    
    def _timer_loop(self):
        """Loop principal do timer."""
        while self.is_running:
            total_seconds = self.get_total_seconds()
            
            if total_seconds <= 0:
                self.stop()
                break
            
            # Contagem regressiva
            remaining = total_seconds
            while remaining > 0 and self.is_running:
                if self.on_next_exec_update:
                    self.on_next_exec_update(f"Próxima execução em: {self.format_time(remaining)}")
                
                time.sleep(1)
                remaining -= 1
            
            if not self.is_running:
                break
            
            # Executa callback
            if self.on_status_update:
                self.on_status_update("Executando reboot...")
            
            if self.on_next_exec_update:
                self.on_next_exec_update("Aguardando conclusão do reboot...")
            
            self.logger.info("Timer disparado - executando reboot automático")
            success = self.callback()
            
            if success:
                self.logger.info("Reboot concluído com sucesso, timer será reiniciado")
            else:
                self.logger.warning("Reboot falhou, timer será reiniciado mesmo assim")
            
            # Reinicia timer
            if self.is_running:
                if self.on_status_update:
                    self.on_status_update("Rodando")
                
                if self.on_next_exec_update:
                    self.on_next_exec_update("Timer reiniciado, aguardando próxima execução...")
                
                time.sleep(2)
                self.logger.info("Timer reiniciado, contagem regressiva iniciada")

