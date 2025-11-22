"""Serviço principal de reboot do WhatsApp."""

import time
from typing import Optional

from src.process_manager.window_manager import WindowManager
from src.process_manager.process_manager import ProcessManager
from src.utils.logger import Logger


class RebootService:
    """Serviço que executa o reboot do WhatsApp."""
    
    def __init__(
        self,
        logger: Logger,
        window_manager: WindowManager,
        process_manager: ProcessManager
    ):
        """
        Inicializa o serviço de reboot.
        
        Args:
            logger: Instância do logger
            window_manager: Gerenciador de janelas
            process_manager: Gerenciador de processos
        """
        self.logger = logger
        self.window_manager = window_manager
        self.process_manager = process_manager
    
    def execute_reboot(self) -> bool:
        """
        Executa o processo completo de reboot do WhatsApp.
        
        Returns:
            True se sucesso, False caso contrário
        """
        self.logger.step(1, "DETECÇÃO DE JANELA", "Procurando janela do WhatsApp...")
        windows = self.window_manager.find_whatsapp_windows()
        
        if not windows:
            self.logger.error("WhatsApp não está aberto!")
            return False
        
        hwnd, window_title = windows[0]
        self.logger.info(f"Janela encontrada: '{window_title}' (HWND: {hwnd})")
        
        self.logger.step(2, "OBTENÇÃO DO CAMINHO", "Obtendo caminho do executável...")
        exe_path = self.process_manager.find_whatsapp_exe_path()
        if not exe_path:
            self.logger.error("Não foi possível encontrar o executável do WhatsApp!")
            return False
        self.logger.info(f"Caminho do executável: {exe_path}")
        
        self.logger.step(3, "CAPTURA DE INFORMAÇÕES", "Capturando informações da janela...")
        window_info = self.window_manager.get_window_info(hwnd)
        if not window_info:
            self.logger.warning("Não foi possível obter informações da janela, tentando carregar salvas...")
            window_info = self.window_manager.load_window_info()
            if not window_info:
                self.logger.error("Não foi possível obter informações da janela!")
                return False
        
        self.window_manager.save_window_info(window_info)
        
        self.logger.step(4, "ENCERRAMENTO DE PROCESSOS", "Encerrando processos do WhatsApp...")
        killed = self.process_manager.kill_whatsapp_processes()
        if not killed:
            self.logger.warning("Nenhum processo do WhatsApp foi encontrado para encerrar!")
            # Continua mesmo assim, pode ser que já esteja fechado
        
        self.process_manager.wait_for_processes_to_end()
        
        self.logger.step(5, "REINÍCIO DO WHATSAPP", "Reiniciando WhatsApp...")
        if not self.process_manager.start_whatsapp(exe_path):
            self.logger.error("Falha ao iniciar o WhatsApp!")
            return False
        
        time.sleep(1)
        
        self.logger.step(6, "RESTAURAÇÃO DA JANELA", "Aguardando janela aparecer e restaurando...")
        new_hwnd = self.window_manager.wait_for_window()
        if not new_hwnd:
            self.logger.error("Janela do WhatsApp não foi encontrada após reinício!")
            return False
        
        time.sleep(0.3)
        
        if not self.window_manager.restore_window(new_hwnd, window_info):
            self.logger.warning("Janela não foi restaurada corretamente, mas WhatsApp foi reiniciado")
            return True  # Considera sucesso parcial
        
        self.logger.step(7, "CONCLUÍDO", "Reboot do WhatsApp concluído com sucesso!")
        return True

