"""Sistema de logging centralizado."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class Logger:
    """Logger centralizado com suporte a arquivo e console."""
    
    def __init__(self, log_file: Optional[str] = None, log_dir: str = "logs"):
        """
        Inicializa o logger.
        
        Args:
            log_file: Nome do arquivo de log (opcional)
            log_dir: Diretório para salvar logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        if log_file is None:
            log_file = f"whatsapp_rebooter_{datetime.now().strftime('%Y%m%d')}.log"
        
        self.log_file = self.log_dir / log_file
        
        # Configura logger
        self.logger = logging.getLogger("WhatsAppRebooter")
        self.logger.setLevel(logging.DEBUG)
        
        # Evita duplicação de handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura handlers de logging."""
        # Handler para arquivo
        file_handler = logging.FileHandler(
            self.log_file, 
            encoding='utf-8',
            mode='a'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Log de debug."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log de informação."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log de aviso."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log de erro."""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """Log crítico."""
        self.logger.critical(message, exc_info=exc_info)
    
    def step(self, step_number: int, step_name: str, message: str = ""):
        """
        Log formatado para passos de execução.
        
        Args:
            step_number: Número do passo
            step_name: Nome do passo
            message: Mensagem adicional
        """
        separator = "=" * 60
        log_msg = f"\n{separator}\n"
        log_msg += f"PASSO {step_number}: {step_name}\n"
        if message:
            log_msg += f"  → {message}\n"
        log_msg += separator
        self.info(log_msg)

