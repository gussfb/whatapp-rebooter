"""Janela principal da aplicação."""

import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Callable
from PIL import Image, ImageTk
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
        
        # Variável para manter referência do ícone (evita garbage collection)
        self.app_icon = None
        self.window_icon_path = None
        
        # Define tema primeiro
        self._setup_theme()
        self._setup_window()
        self._create_ui()
        self._setup_callbacks()
        self._setup_window_handlers()
        
        # Inicia processamento de log em tempo real
        self._process_log_queue()
        
        # Carrega ícone após a janela estar totalmente criada (múltiplas tentativas)
        self.root.after(50, self._load_window_icon)
        self.root.after(200, self._load_window_icon)  # Segunda tentativa
        self.root.after(500, self._load_window_icon)  # Terceira tentativa
        
        self.logger.info("Aplicativo iniciado")
        self.logger.info(f"PID do aplicativo: {os.getpid()}")
        
        # Verifica se deve iniciar automaticamente
        self._check_auto_start()
    
    def _setup_theme(self):
        """Configura tema e cores da aplicação."""
        # Cores modernas
        self.colors = {
            'bg_main': '#f5f5f5',
            'bg_frame': '#ffffff',
            'bg_highlight': '#e3f2fd',
            'primary': '#25D366',  # Verde WhatsApp
            'primary_dark': '#128C7E',
            'secondary': '#2196F3',
            'danger': '#f44336',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'border': '#e0e0e0'
        }
        
        # Fontes modernas (tenta Segoe UI, fallback para Arial)
        try:
            self.font_title = ("Segoe UI", 20, "bold")
            self.font_subtitle = ("Segoe UI", 11, "bold")
            self.font_normal = ("Segoe UI", 10)
            self.font_small = ("Segoe UI", 9)
            self.font_mono = ("Consolas", 9)
        except:
            self.font_title = ("Arial", 18, "bold")
            self.font_subtitle = ("Arial", 11, "bold")
            self.font_normal = ("Arial", 10)
            self.font_small = ("Arial", 9)
            self.font_mono = ("Consolas", 9)
        
        # Aplica cor de fundo
        self.root.configure(bg=self.colors['bg_main'])
    
    def _setup_window(self):
        """Configura a janela principal."""
        self.root.title("WhatsApp Rebooter")
        self.root.geometry("700x750")
        self.root.resizable(True, True)
        self.root.attributes('-topmost', False)
        
        # Tenta carregar ícone imediatamente (fallback rápido)
        self._try_quick_icon_load()
    
    def _load_app_icon(self):
        """Carrega ícone para exibir na interface."""
        try:
            # Tenta carregar PNG para exibir na interface
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            possible_paths = [
                os.path.join(base_dir, "assets", "whatsapprebooter.png"),
                os.path.join(base_dir, "assets", "icon_256.png"),
                os.path.join(base_dir, "assets", "icon_512.png"),
                os.path.join(os.getcwd(), "assets", "whatsapprebooter.png"),
                os.path.join(os.getcwd(), "assets", "icon_256.png"),
                os.path.join(os.getcwd(), "assets", "icon_512.png"),
            ]
            
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(os.path.normpath(path))
                    if os.path.exists(abs_path) and os.path.isfile(abs_path):
                        # Carrega e redimensiona para 64x64
                        img = Image.open(abs_path)
                        img = img.resize((48, 48), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.logger.info(f"Ícone da interface carregado: {abs_path}")
                        return photo
                except Exception as e:
                    self.logger.debug(f"Erro ao carregar {path}: {e}")
                    continue
        except Exception as e:
            self.logger.debug(f"Erro ao carregar ícone da interface: {e}")
        
        return None
    
    def _try_quick_icon_load(self):
        """Tentativa rápida de carregar ícone."""
        try:
            # Tenta caminhos comuns
            quick_paths = [
                os.path.join(os.getcwd(), "assets", "icon.ico"),
                "assets/icon.ico",
                os.path.abspath("assets/icon.ico")
            ]
            
            for path in quick_paths:
                try:
                    abs_path = os.path.abspath(os.path.normpath(path))
                    if os.path.exists(abs_path) and os.path.isfile(abs_path):
                        self.root.iconbitmap(abs_path)
                        self.window_icon_path = abs_path
                        self.logger.info(f"Ícone carregado rapidamente: {abs_path}")
                        return
                except:
                    continue
        except:
            pass
    
    def _load_window_icon(self):
        """Carrega o ícone na janela (barra de título e barra de tarefas)."""
        try:
            # Se estiver rodando como executável, o ícone já está embutido
            # Mas ainda precisamos definir para a janela
            
            # Tenta múltiplos caminhos possíveis
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            possible_paths = [
                os.path.join(base_dir, "assets", "icon.ico"),
                os.path.join(os.getcwd(), "assets", "icon.ico"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "icon.ico"),
                os.path.abspath("assets/icon.ico"),
                os.path.normpath(os.path.join(os.getcwd(), "assets", "icon.ico"))
            ]
            
            icon_path = None
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(os.path.normpath(path))
                    if os.path.exists(abs_path) and os.path.isfile(abs_path):
                        icon_path = abs_path
                        self.window_icon_path = abs_path
                        self.logger.info(f"Ícone encontrado: {icon_path}")
                        break
                except:
                    continue
            
            if not icon_path:
                # Se não encontrou, tenta usar o caminho já carregado
                if self.window_icon_path:
                    icon_path = self.window_icon_path
                else:
                    self.logger.warning("Ícone não encontrado em nenhum dos caminhos testados")
                    return
            
            # Aguarda a janela estar totalmente criada
            self.root.update_idletasks()
            self.root.update()
            
            # Método 1: iconbitmap (deve funcionar para barra de título)
            try:
                self.root.iconbitmap(icon_path)
                self.logger.info(f"Ícone definido via iconbitmap: {icon_path}")
            except Exception as e1:
                self.logger.warning(f"Erro com iconbitmap: {e1}")
            
            # Método 2: win32gui (mais confiável para Windows, define ambos os ícones)
            try:
                import sys
                # Obtém HWND da janela
                hwnd = self.root.winfo_id()
                # Para Tkinter no Windows, precisa obter o HWND real
                try:
                    hwnd = win32gui.GetParent(hwnd)
                    if hwnd == 0:
                        hwnd = self.root.winfo_id()
                except:
                    pass
                
                # Converte caminho para formato Windows
                icon_path_win = os.path.normpath(icon_path).replace('/', '\\')
                
                # Carrega ícone grande (32x32) para barra de título
                large_icon = win32gui.LoadImage(
                    0,
                    icon_path_win,
                    win32con.IMAGE_ICON,
                    32, 32,
                    win32con.LR_LOADFROMFILE
                )
                
                # Carrega ícone pequeno (16x16) para barra de tarefas
                small_icon = win32gui.LoadImage(
                    0,
                    icon_path_win,
                    win32con.IMAGE_ICON,
                    16, 16,
                    win32con.LR_LOADFROMFILE
                )
                
                # Define os ícones
                win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, large_icon)
                win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, small_icon)
                
                self.logger.info(f"Ícone definido via win32gui: {icon_path_win}")
            except Exception as e2:
                self.logger.warning(f"Erro com win32gui: {e2}")
                import traceback
                self.logger.debug(traceback.format_exc())
                
        except Exception as e:
            self.logger.warning(f"Erro geral ao carregar ícone: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
    
    def _create_ui(self):
        """Cria a interface do usuário."""
        # Header compacto com título e ícone
        header_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        header_frame.pack(fill="x", pady=(8, 5))
        
        # Container para ícone e título lado a lado
        title_container = tk.Frame(header_frame, bg=self.colors['bg_main'])
        title_container.pack()
        
        # Carrega e exibe ícone (menor)
        self.app_icon = self._load_app_icon()
        if self.app_icon:
            icon_label = tk.Label(
                title_container,
                image=self.app_icon,
                bg=self.colors['bg_main']
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Título (menor)
        title_label = tk.Label(
            title_container,
            text="WhatsApp Rebooter",
            font=("Segoe UI", 16, "bold") if "Segoe UI" in str(self.font_title) else ("Arial", 16, "bold"),
            bg=self.colors['bg_main'],
            fg=self.colors['primary_dark']
        )
        title_label.pack(side=tk.LEFT)
        
        # Frame de configuração do timer
        self._create_timer_frame()
        
        # Status e próxima execução em uma linha
        status_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        status_frame.pack(pady=8, fill="x")
        
        # Status à esquerda
        status_container = tk.Frame(status_frame, bg=self.colors['bg_main'])
        status_container.pack(side=tk.LEFT, padx=20)
        
        status_title = tk.Label(
            status_container,
            text="Status:",
            font=self.font_small,
            bg=self.colors['bg_main'],
            fg=self.colors['text_secondary']
        )
        status_title.pack(side=tk.LEFT, padx=(0, 3))
        
        self.status_label = tk.Label(
            status_container,
            text="Parado",
            fg=self.colors['danger'],
            font=self.font_small,
            bg=self.colors['bg_main']
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Próxima execução à direita
        next_exec_container = tk.Frame(status_frame, bg=self.colors['bg_main'])
        next_exec_container.pack(side=tk.RIGHT, padx=20)
        
        next_exec_title = tk.Label(
            next_exec_container,
            text="⏳ Próxima:",
            font=self.font_small,
            bg=self.colors['bg_main'],
            fg=self.colors['text_secondary']
        )
        next_exec_title.pack(side=tk.LEFT, padx=(0, 3))
        
        self.next_exec_label = tk.Label(
            next_exec_container,
            text="--",
            font=self.font_small,
            bg=self.colors['bg_main'],
            fg=self.colors['primary_dark']
        )
        self.next_exec_label.pack(side=tk.LEFT)
        
        # Botões
        self._create_buttons()
        
        # Área de log
        self._create_log_area()
    
    def _create_timer_frame(self):
        """Cria frame de configuração do Timer."""
        timer_frame = tk.LabelFrame(
            self.root,
            text="⏱️ Configuração do Timer",
            font=self.font_small,
            bg=self.colors['bg_frame'],
            fg=self.colors['text_primary'],
            padx=12,
            pady=10,
            relief=tk.FLAT,
            bd=1,
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        timer_frame.pack(pady=8, padx=20, fill="x")
        timer_frame.configure(bg=self.colors['bg_frame'])
        
        # Carrega configurações salvas
        user_settings = self.config.get_user_settings()
        
        # Container compacto para os inputs - tudo em uma linha
        inputs_container = tk.Frame(timer_frame, bg=self.colors['bg_highlight'], relief=tk.RAISED, bd=2)
        inputs_container.pack(pady=8, padx=8, fill="x")
        
        # Horas - compacto
        hours_frame = tk.Frame(inputs_container, bg=self.colors['bg_highlight'])
        hours_frame.pack(side=tk.LEFT, padx=10, pady=6)
        
        hours_label = tk.Label(
            hours_frame,
            text="🕐 Horas:",
            font=self.font_normal,
            bg=self.colors['bg_highlight'],
            fg=self.colors['primary_dark']
        )
        hours_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.hours_var = tk.StringVar(value=str(user_settings.get("timer_hours", 4)))
        self.hours_var.trace_add("write", lambda *args: self._save_user_settings())
        hours_spinbox = tk.Spinbox(
            hours_frame,
            from_=0,
            to=23,
            textvariable=self.hours_var,
            width=5,
            font=self.font_normal,
            bg="white",
            relief=tk.SUNKEN,
            bd=2
        )
        hours_spinbox.pack(side=tk.LEFT)
        
        # Separador visual
        separator1 = tk.Label(
            inputs_container,
            text="|",
            font=self.font_small,
            bg=self.colors['bg_highlight'],
            fg=self.colors['text_secondary']
        )
        separator1.pack(side=tk.LEFT, padx=5)
        
        # Minutos - compacto
        minutes_frame = tk.Frame(inputs_container, bg=self.colors['bg_highlight'])
        minutes_frame.pack(side=tk.LEFT, padx=10, pady=6)
        
        minutes_label = tk.Label(
            minutes_frame,
            text="⏰ Minutos:",
            font=self.font_normal,
            bg=self.colors['bg_highlight'],
            fg=self.colors['primary_dark']
        )
        minutes_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.minutes_var = tk.StringVar(value=str(user_settings.get("timer_minutes", 0)))
        self.minutes_var.trace_add("write", lambda *args: self._save_user_settings())
        minutes_spinbox = tk.Spinbox(
            minutes_frame,
            from_=0,
            to=59,
            textvariable=self.minutes_var,
            width=5,
            font=self.font_normal,
            bg="white",
            relief=tk.SUNKEN,
            bd=2
        )
        minutes_spinbox.pack(side=tk.LEFT)
        
        # Separador visual
        separator2 = tk.Label(
            inputs_container,
            text="|",
            font=self.font_small,
            bg=self.colors['bg_highlight'],
            fg=self.colors['text_secondary']
        )
        separator2.pack(side=tk.LEFT, padx=5)
        
        # Segundos - compacto
        seconds_frame = tk.Frame(inputs_container, bg=self.colors['bg_highlight'])
        seconds_frame.pack(side=tk.LEFT, padx=10, pady=6)
        
        seconds_label = tk.Label(
            seconds_frame,
            text="⏱️ Segundos:",
            font=self.font_normal,
            bg=self.colors['bg_highlight'],
            fg=self.colors['primary_dark']
        )
        seconds_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.seconds_var = tk.StringVar(value=str(user_settings.get("timer_seconds", 0)))
        self.seconds_var.trace_add("write", lambda *args: self._save_user_settings())
        seconds_spinbox = tk.Spinbox(
            seconds_frame,
            from_=0,
            to=59,
            textvariable=self.seconds_var,
            width=5,
            font=self.font_normal,
            bg="white",
            relief=tk.SUNKEN,
            bd=2
        )
        seconds_spinbox.pack(side=tk.LEFT)
        
        # Checkbox para auto-start
        auto_start_frame = tk.Frame(timer_frame, bg=self.colors['bg_frame'])
        auto_start_frame.pack(pady=(8, 3))
        
        self.auto_start_var = tk.BooleanVar(value=user_settings.get("auto_start_on_detection", True))
        self.auto_start_var.trace_add("write", lambda *args: self._save_user_settings())
        
        auto_start_check = tk.Checkbutton(
            auto_start_frame,
            text="✅ Iniciar automaticamente ao detectar WhatsApp",
            variable=self.auto_start_var,
            font=self.font_normal,
            bg=self.colors['bg_frame'],
            fg=self.colors['text_primary'],
            activebackground=self.colors['bg_frame'],
            activeforeground=self.colors['text_primary'],
            selectcolor="white"
        )
        auto_start_check.pack()
    
    def _create_buttons(self):
        """Cria botões de controle."""
        button_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        button_frame.pack(pady=10, padx=20)
        
        # Botão único de Start/Stop
        self.toggle_button = tk.Button(
            button_frame,
            text="▶️ Start",
            command=self._on_toggle,
            bg=self.colors['success'],
            fg="white",
            font=self.font_normal,
            width=14,
            height=1,
            relief=tk.RAISED,
            cursor="hand2",
            activebackground="#45a049",
            activeforeground="white",
            bd=3,
            padx=8,
            pady=4,
            highlightthickness=0
        )
        self.toggle_button.pack(side=tk.LEFT, padx=8)
        self._add_button_click_effect(self.toggle_button)
        
        self.test_button = tk.Button(
            button_frame,
            text="🧪 Testar Agora",
            command=self._on_test,
            bg=self.colors['secondary'],
            fg="white",
            font=self.font_normal,
            width=14,
            height=1,
            relief=tk.RAISED,
            cursor="hand2",
            activebackground="#0b7dda",
            activeforeground="white",
            bd=3,
            padx=8,
            pady=4,
            highlightthickness=0
        )
        self.test_button.pack(side=tk.LEFT, padx=8)
        self._add_button_click_effect(self.test_button)
    
    def _add_button_click_effect(self, button):
        """Adiciona efeito visual de click ao botão."""
        def on_press(event):
            button.config(relief=tk.SUNKEN)
        
        def on_release(event):
            button.config(relief=tk.RAISED)
        
        button.bind("<Button-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)
    
    def _create_log_area(self):
        """Cria área de log."""
        log_frame = tk.LabelFrame(
            self.root,
            text="📋 Log de Atividades",
            font=self.font_small,
            bg=self.colors['bg_frame'],
            fg=self.colors['text_primary'],
            padx=10,
            pady=8,
            relief=tk.FLAT,
            bd=1,
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        log_frame.pack(pady=8, padx=20, fill="both", expand=True)
        log_frame.configure(bg=self.colors['bg_frame'])
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=24,
            width=80,
            font=self.font_mono,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            relief=tk.SUNKEN,
            bd=2,
            wrap=tk.WORD
        )
        self.log_text.pack(fill="both", expand=True, pady=(0, 5))
        
        clear_log_btn = tk.Button(
            log_frame,
            text="🗑️ Limpar Log",
            command=self._clear_log,
            bg=self.colors['text_secondary'],
            fg="white",
            font=self.font_small,
            relief=tk.RAISED,
            cursor="hand2",
            activebackground="#616161",
            activeforeground="white",
            bd=0,
            padx=10,
            pady=3
        )
        clear_log_btn.pack()
    
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
        """Atualiza label de status e botão toggle."""
        if status == "Parado":
            self.status_label.config(text="Parado", fg=self.colors['danger'])
            self._update_toggle_button(False)
        elif status == "Rodando":
            self.status_label.config(text="Rodando", fg=self.colors['success'])
            self._update_toggle_button(True)
        elif "Executando" in status:
            self.status_label.config(text=status, fg=self.colors['warning'])
            # Mantém o estado do botão durante execução
    
    def _update_toggle_button(self, is_running: bool):
        """Atualiza o botão toggle conforme o estado."""
        if is_running:
            self.toggle_button.config(
                text="⏹️ Stop",
                bg=self.colors['danger'],
                activebackground="#da190b"
            )
        else:
            self.toggle_button.config(
                text="▶️ Start",
                bg=self.colors['success'],
                activebackground="#45a049"
            )
    
    def _update_next_exec(self, text: str):
        """Atualiza label de próxima execução."""
        self.next_exec_label.config(text=text)
    
    def _on_toggle(self):
        """Handler do botão toggle Start/Stop."""
        if self.timer_service.is_running:
            # Se está rodando, para
            self.timer_service.stop()
        else:
            # Se está parado, inicia
            try:
                hours = int(self.hours_var.get())
                minutes = int(self.minutes_var.get())
                seconds = int(self.seconds_var.get())
                
                # Salva configurações
                self._save_user_settings()
                
                self.timer_service.set_timer(hours, minutes, seconds)
                
                if not self.timer_service.start():
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
                        # O botão será atualizado automaticamente via _update_status
                        pass
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


