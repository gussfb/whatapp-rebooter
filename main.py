"""Ponto de entrada principal da aplicação."""

import tkinter as tk
import win32gui

from src.core.reboot_service import RebootService
from src.core.timer_service import TimerService
from src.process_manager.window_manager import WindowManager
from src.process_manager.process_manager import ProcessManager
from src.ui.main_window import MainWindow, UILogHandler
from src.utils.config import Config
from src.utils.logger import Logger


def main():
    """Função principal da aplicação."""
    # Inicializa componentes
    config = Config()
    logger = Logger()
    
    # Cria serviços
    window_manager = WindowManager(logger, config)
    process_manager = ProcessManager(logger, config)
    reboot_service = RebootService(logger, window_manager, process_manager)
    timer_service = TimerService(logger, reboot_service.execute_reboot)
    
    # Cria interface
    root = tk.Tk()
    
    # Obtém HWND da aplicação para evitar detectá-la
    try:
        app_hwnd = root.winfo_id()
        app_hwnd = win32gui.GetParent(app_hwnd) if win32gui.GetParent(app_hwnd) else app_hwnd
        window_manager.set_app_hwnd(app_hwnd)
    except (AttributeError, RuntimeError):
        # Silencia erro se HWND não estiver disponível ainda
        pass
    
    # Cria janela principal
    main_window = MainWindow(root, logger, reboot_service, timer_service, config)
    
    # Conecta logger com UI
    ui_handler = UILogHandler(logger, main_window.log_to_ui)
    
    # Inicia loop principal
    root.mainloop()


if __name__ == "__main__":
    main()

