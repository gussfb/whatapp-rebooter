"""Gerenciamento de janelas do Windows."""

import json
import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

import win32gui
import win32con
import win32process

from src.utils.logger import Logger


class WindowManager:
    """Gerencia janelas do Windows."""
    
    def __init__(self, logger: Logger, config):
        """
        Inicializa o gerenciador de janelas.
        
        Args:
            logger: Instância do logger
            config: Instância de configurações
        """
        self.logger = logger
        self.config = config
        self.window_info_file = Path(config.get_window_info_file())
        self.app_hwnd: Optional[int] = None
    
    def set_app_hwnd(self, hwnd: int):
        """Define o HWND da aplicação para evitar detectá-la."""
        self.app_hwnd = hwnd
    
    def find_whatsapp_windows(self) -> List[Tuple[int, str]]:
        """
        Encontra todas as janelas do WhatsApp.
        
        Returns:
            Lista de tuplas (hwnd, window_title)
        """
        self.logger.info("Procurando janelas do WhatsApp...")
        
        windows = []
        
        def callback(hwnd, windows_list):
            # Ignora a janela da própria aplicação
            if self.app_hwnd and hwnd == self.app_hwnd:
                return
            
            if not win32gui.IsWindowVisible(hwnd):
                return
            
            window_text = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            
            # Ignora janelas do rebooter
            if "rebooter" in window_text.lower() or "rebooter" in class_name.lower():
                return
            
            # Verifica se é janela do WhatsApp
            if "whatsapp" in window_text.lower() or "whatsapp" in class_name.lower():
                windows_list.append((hwnd, window_text))
        
        win32gui.EnumWindows(callback, windows)
        
        if not windows:
            self.logger.warning("Nenhuma janela do WhatsApp encontrada")
        else:
            self.logger.info(f"Encontradas {len(windows)} janela(s) do WhatsApp")
        
        return windows
    
    def get_window_info(self, hwnd: int) -> Optional[Dict[str, Any]]:
        """
        Obtém informações da janela (posição, tamanho, estado).
        
        Args:
            hwnd: Handle da janela
            
        Returns:
            Dicionário com informações da janela ou None
        """
        try:
            rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top
            
            placement = win32gui.GetWindowPlacement(hwnd)
            is_minimized = placement[1] == win32con.SW_SHOWMINIMIZED
            
            info = {
                'left': left,
                'top': top,
                'width': width,
                'height': height,
                'is_minimized': is_minimized
            }
            
            self.logger.debug(
                f"Janela: Pos({left}, {top}) Tamanho({width}x{height}) "
                f"Minimizada={is_minimized}"
            )
            
            return info
        except Exception as e:
            self.logger.error(f"Erro ao obter informações da janela: {e}", exc_info=True)
            return None
    
    def save_window_info(self, window_info: Dict[str, Any]):
        """
        Salva informações da janela em arquivo JSON.
        
        Args:
            window_info: Dicionário com informações da janela
        """
        try:
            with open(self.window_info_file, 'w', encoding='utf-8') as f:
                json.dump(window_info, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Informações da janela salvas em {self.window_info_file}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar informações da janela: {e}", exc_info=True)
    
    def load_window_info(self) -> Optional[Dict[str, Any]]:
        """
        Carrega informações da janela do arquivo JSON.
        
        Returns:
            Dicionário com informações da janela ou None
        """
        if not self.window_info_file.exists():
            return None
        
        try:
            with open(self.window_info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            self.logger.info(f"Informações da janela carregadas de {self.window_info_file}")
            return info
        except Exception as e:
            self.logger.error(f"Erro ao carregar informações da janela: {e}", exc_info=True)
            return None
    
    def restore_window(self, hwnd: int, window_info: Dict[str, Any]) -> bool:
        """
        Restaura janela na posição e tamanho salvos.
        
        Args:
            hwnd: Handle da janela
            window_info: Informações da janela a restaurar
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Restaura se estava minimizada
            if window_info.get('is_minimized', False):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                import time
                time.sleep(0.1)
            
            # Restaura posição e tamanho
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,
                window_info['left'],
                window_info['top'],
                window_info['width'],
                window_info['height'],
                win32con.SWP_SHOWWINDOW
            )
            
            import time
            time.sleep(0.1)
            
            # Verifica se foi restaurada corretamente
            rect = win32gui.GetWindowRect(hwnd)
            if rect[0] == window_info['left'] and rect[1] == window_info['top']:
                self.logger.info("Janela restaurada com sucesso")
                return True
            else:
                self.logger.warning("Janela restaurada, mas posição pode estar incorreta")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao restaurar janela: {e}", exc_info=True)
            return False
    
    def wait_for_window(self, max_attempts: int = 120) -> Optional[int]:
        """
        Aguarda janela do WhatsApp aparecer.
        
        Args:
            max_attempts: Número máximo de tentativas
            
        Returns:
            HWND da janela encontrada ou None
        """
        import time
        
        self.logger.info("Aguardando janela do WhatsApp aparecer...")
        interval = self.config.get("window_detection_interval", 0.3)
        
        for attempt in range(max_attempts):
            time.sleep(interval)
            windows = self.find_whatsapp_windows()
            
            if windows:
                hwnd = windows[0][0]
                elapsed = attempt * interval
                self.logger.info(f"Janela encontrada após {elapsed:.1f} segundo(s)")
                return hwnd
            
            if attempt > 0 and attempt % 20 == 0:
                elapsed = attempt * interval
                self.logger.debug(f"Aguardando... ({elapsed:.0f}s)")
        
        self.logger.error("Janela do WhatsApp não foi encontrada")
        return None

