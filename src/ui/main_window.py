"""Janela principal da aplicação."""

import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Callable
import win32gui
import win32con

from src.core.reboot_service import RebootService
from src.core.timer_service import TimerService
from src.utils.logger import Logger


class MainWindow:
    """Janela principal da aplicação."""
    
    def __init__(
        self,
        root: tk.Tk,
        logger: Logger,
        reboot_service: RebootService,
        timer_service: TimerService,
        config=None
    ):
        """
        Inicializa a janela principal.
        
        Args:
            root: Instância do Tk root
            logger: Instância do logger
            reboot_service: Serviço de reboot
            timer_service: Serviço de timer
            config: Instância de Config (opcional)
        """
        self.root = root
        self.logger = logger
        self.reboot_service = reboot_service
        self.timer_service = timer_service
        
        # Importa Config se não fornecido
        if config is None:
            from src.utils.config import Config
            self.config = Config()
        else:
            self.config = config
        
        # Fila para atualizações thread-safe da UI
        self.log_queue = queue.Queue()
        
        self._setup_window()
        self._create_ui()
        self._setup_callbacks()
        self._setup_window_handlers()
        
        # Inicia processamento de log em tempo real
        self._process_log_queue()
        
        self.logger.info("Aplicativo iniciado")
        self.logger.info(f"PID do aplicativo: {os.getpid()}")
        
        # Verifica se deve iniciar automaticamente
        self._check_auto_start()
    
    def _setup_window(self):
        """Configura a janela principal."""
        self.root.title("WhatsApp Rebooter")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        self.root.attributes('-topmost', False)
    
    def _create_ui(self):
        """Cria a interface do usuário."""
        # Título
        title_label = tk.Label(
            self.root,
            text="WhatsApp Rebooter",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=15)
        
        # Frame de configuração do timer
        self._create_timer_frame()
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="Status: Parado",
            fg="red",
            font=("Arial", 11, "bold")
        )
        self.status_label.pack(pady=10)
        
        # Próxima execução
        self.next_exec_label = tk.Label(
            self.root,
            text="Próxima execução: --",
            font=("Arial", 9)
        )
        self.next_exec_label.pack(pady=5)
        
        # Botões
        self._create_buttons()
        
        # Área de log
        self._create_log_area()
    
    def _create_timer_frame(self):
        """Cria frame de configuração do timer."""
        timer_frame = tk.LabelFrame(
            self.root,
            text="Configuração do Timer",
            padx=15,
            pady=15
        )
        timer_frame.pack(pady=15, padx=25, fill="x")
        
        # Carrega configurações salvas
        user_settings = self.config.get_user_settings()
        
        # Horas
        hours_frame = tk.Frame(timer_frame)
        hours_frame.pack(pady=5)
        tk.Label(hours_frame, text="Horas:", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        self.hours_var = tk.StringVar(value=str(user_settings.get("timer_hours", 4)))
        self.hours_var.trace_add("write", lambda *args: self._save_user_settings())
        tk.Spinbox(hours_frame, from_=0, to=23, textvariable=self.hours_var, width=8).pack(side=tk.LEFT)
        
        # Minutos
        minutes_frame = tk.Frame(timer_frame)
        minutes_frame.pack(pady=5)
        tk.Label(minutes_frame, text="Minutos:", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        self.minutes_var = tk.StringVar(value=str(user_settings.get("timer_minutes", 0)))
        self.minutes_var.trace_add("write", lambda *args: self._save_user_settings())
        tk.Spinbox(minutes_frame, from_=0, to=59, textvariable=self.minutes_var, width=8).pack(side=tk.LEFT)
        
        # Segundos
        seconds_frame = tk.Frame(timer_frame)
        seconds_frame.pack(pady=5)
        tk.Label(seconds_frame, text="Segundos:", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        self.seconds_var = tk.StringVar(value=str(user_settings.get("timer_seconds", 0)))
        self.seconds_var.trace_add("write", lambda *args: self._save_user_settings())
        tk.Spinbox(seconds_frame, from_=0, to=59, textvariable=self.seconds_var, width=8).pack(side=tk.LEFT)
        
        # Checkbox para auto-start
        auto_start_frame = tk.Frame(timer_frame)
        auto_start_frame.pack(pady=5)
        self.auto_start_var = tk.BooleanVar(value=user_settings.get("auto_start_on_detection", True))
        self.auto_start_var.trace_add("write", lambda *args: self._save_user_settings())
        tk.Checkbutton(
            auto_start_frame,
            text="Iniciar automaticamente ao detectar WhatsApp",
            variable=self.auto_start_var
        ).pack(side=tk.LEFT)
    
    def _create_buttons(self):
        """Cria botões de controle."""
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=25, padx=20)
        
        self.start_button = tk.Button(
            button_frame,
            text="Iniciar",
            command=self._on_start,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=2,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=8)
        
        self.stop_button = tk.Button(
            button_frame,
            text="Parar",
            command=self._on_stop,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=2,
            state=tk.DISABLED,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.stop_button.pack(side=tk.LEFT, padx=8)
        
        self.test_button = tk.Button(
            button_frame,
            text="Testar Agora",
            command=self._on_test,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=2,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.test_button.pack(side=tk.LEFT, padx=8)
    
    def _create_log_area(self):
        """Cria área de log."""
        log_frame = tk.LabelFrame(
            self.root,
            text="Log de Atividades",
            padx=10,
            pady=10
        )
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            width=80,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white"
        )
        self.log_text.pack(fill="both", expand=True)
        
        clear_log_btn = tk.Button(
            log_frame,
            text="Limpar Log",
            command=self._clear_log,
            bg="#666",
            fg="white",
            font=("Arial", 8)
        )
        clear_log_btn.pack(pady=5)
    
    def _setup_callbacks(self):
        """Configura callbacks do timer service."""
        # Wrappers thread-safe para atualizar UI
        self.timer_service.on_status_update = lambda status: self.root.after(0, lambda: self._update_status(status))
        self.timer_service.on_next_exec_update = lambda text: self.root.after(0, lambda: self._update_next_exec(text))
    
    def _setup_window_handlers(self):
        """Configura handlers da janela."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.after(100, self._ensure_window_visible)
    
    def _update_status(self, status: str):
        """Atualiza label de status."""
        if status == "Parado":
            self.status_label.config(text="Status: Parado", fg="red")
        elif status == "Rodando":
            self.status_label.config(text="Status: Rodando", fg="green")
        elif "Executando" in status:
            self.status_label.config(text=f"Status: {status}", fg="orange")
    
    def _update_next_exec(self, text: str):
        """Atualiza label de próxima execução."""
        self.next_exec_label.config(text=text)
    
    def _on_start(self):
        """Handler do botão Iniciar."""
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            seconds = int(self.seconds_var.get())
            
            # Salva configurações
            self._save_user_settings()
            
            self.timer_service.set_timer(hours, minutes, seconds)
            
            if self.timer_service.start():
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
            else:
                messagebox.showwarning(
                    "Aviso",
                    "Configure um timer válido (maior que zero)!"
                )
        except ValueError:
            messagebox.showwarning("Aviso", "Valores inválidos no timer!")
    
    def _save_user_settings(self):
        """Salva configurações do usuário."""
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            seconds = int(self.seconds_var.get())
            auto_start = self.auto_start_var.get()
            
            self.config.save_user_settings(hours, minutes, seconds, auto_start)
        except ValueError:
            pass  # Ignora se valores não forem válidos ainda
    
    def _on_stop(self):
        """Handler do botão Parar."""
        self.timer_service.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def _on_test(self):
        """Handler do botão Testar Agora."""
        if self.timer_service.is_running:
            self.logger.warning("Timer está rodando, não é possível testar agora")
            messagebox.showinfo("Info", "Pare o timer antes de testar!")
            return
        
        # Desabilita botão durante execução
        self.test_button.config(state=tk.DISABLED)
        self.logger.info("Teste manual iniciado pelo usuário")
        
        # Executa reboot em thread separada para não bloquear UI
        def run_reboot():
            try:
                success = self.reboot_service.execute_reboot()
                # Agenda atualização da UI na thread principal
                self.root.after(0, lambda: self._on_reboot_complete(success))
            except Exception as e:
                self.logger.error(f"Erro durante reboot: {e}", exc_info=True)
                self.root.after(0, lambda: self._on_reboot_complete(False))
        
        thread = threading.Thread(target=run_reboot, daemon=True)
        thread.start()
    
    def _on_reboot_complete(self, success: bool):
        """Callback chamado quando reboot completa."""
        self.test_button.config(state=tk.NORMAL)
        if not success:
            messagebox.showwarning(
                "Aviso",
                "Reboot falhou. Verifique o log para mais detalhes."
            )
    
    def _clear_log(self):
        """Limpa a área de log."""
        self.log_text.delete(1.0, tk.END)
        self.logger.info("Log limpo pelo usuário")
    
    def log_to_ui(self, message: str):
        """
        Adiciona mensagem ao log da UI de forma thread-safe.
        
        Args:
            message: Mensagem a ser adicionada
        """
        # Adiciona à fila para processamento na thread principal
        self.log_queue.put(message)
    
    def _process_log_queue(self):
        """Processa mensagens da fila de log na thread principal."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
                # Força atualização imediata
                self.root.update_idletasks()
        except queue.Empty:
            pass
        finally:
            # Agenda próxima verificação
            self.root.after(10, self._process_log_queue)
    
    def _ensure_window_visible(self):
        """Garante que a janela esteja visível."""
        try:
            hwnd = self.root.winfo_id()
            hwnd = win32gui.GetParent(hwnd) if win32gui.GetParent(hwnd) else hwnd
            
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                self.logger.debug("Janela do aplicativo restaurada (estava minimizada)")
        except Exception:
            pass
    
    def _check_auto_start(self):
        """Verifica se deve iniciar o timer automaticamente."""
        user_settings = self.config.get_user_settings()
        if not user_settings.get("auto_start_on_detection", True):
            return
        
        # Verifica se WhatsApp está rodando
        def check_and_start():
            try:
                windows = self.reboot_service.window_manager.find_whatsapp_windows()
                if windows:
                    self.logger.info("WhatsApp detectado - iniciando timer automaticamente")
                    hours = int(self.hours_var.get())
                    minutes = int(self.minutes_var.get())
                    seconds = int(self.seconds_var.get())
                    
                    self.timer_service.set_timer(hours, minutes, seconds)
                    if self.timer_service.start():
                        self.start_button.config(state=tk.DISABLED)
                        self.stop_button.config(state=tk.NORMAL)
                else:
                    self.logger.debug("WhatsApp não detectado - aguardando...")
                    # Tenta novamente após 5 segundos
                    self.root.after(5000, check_and_start)
            except Exception as e:
                self.logger.debug(f"Erro ao verificar auto-start: {e}")
        
        # Aguarda um pouco antes de verificar (para UI carregar)
        self.root.after(1000, check_and_start)
    
    def _on_closing(self):
        """Handler de fechamento da janela."""
        # Salva configurações antes de fechar
        self._save_user_settings()
        
        if self.timer_service.is_running:
            if messagebox.askokcancel(
                "Sair",
                "O timer está rodando. Deseja realmente sair?"
            ):
                self.timer_service.stop()
                self.logger.info("Aplicativo fechado pelo usuário")
                self.root.destroy()
        else:
            self.logger.info("Aplicativo fechado pelo usuário")
            self.root.destroy()


# Adapter para conectar logger com UI
class UILogHandler:
    """Handler de log que também atualiza a UI."""
    
    def __init__(self, logger: Logger, ui_log_callback: Callable[[str], None]):
        """
        Inicializa o handler.
        
        Args:
            logger: Logger original
            ui_log_callback: Função para atualizar UI
        """
        self.logger = logger
        self.ui_callback = ui_log_callback
        
        # Intercepta chamadas do logger
        self._wrap_logger_methods()
    
    def _wrap_logger_methods(self):
        """Envolve métodos do logger para também atualizar UI."""
        original_info = self.logger.info
        original_warning = self.logger.warning
        original_error = self.logger.error
        original_debug = self.logger.debug
        original_step = getattr(self.logger, 'step', None)
        
        def info_wrapper(message: str):
            original_info(message)
            self.ui_callback(f"[INFO] {message}\n")
        
        def warning_wrapper(message: str):
            original_warning(message)
            self.ui_callback(f"[WARNING] {message}\n")
        
        def error_wrapper(message: str, exc_info: bool = False):
            original_error(message, exc_info)
            self.ui_callback(f"[ERROR] {message}\n")
        
        def debug_wrapper(message: str):
            original_debug(message)
            # Debug não aparece na UI por padrão
        
        def step_wrapper(step_number: int, step_name: str, message: str = ""):
            if original_step:
                original_step(step_number, step_name, message)
            # step() já chama info(), então não precisa duplicar
        
        self.logger.info = info_wrapper
        self.logger.warning = warning_wrapper
        self.logger.error = error_wrapper
        self.logger.debug = debug_wrapper
        if original_step:
            self.logger.step = step_wrapper

