import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import win32gui
import win32process
import win32con
import win32api
import psutil
import subprocess
import threading
import time
import json
import os
from datetime import datetime

class WhatsAppRebooter:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Rebooter")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Variáveis
        self.is_running = False
        self.timer_thread = None
        self.window_info_file = "whatsapp_window_info.json"
        self.log_file = "whatsapp_rebooter.log"
        self.current_pid = os.getpid()  # PID do próprio processo
        
        # Interface
        self.create_ui()
        
        # Garante que a janela fique sempre visível
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Mantém a janela sempre visível (não minimiza)
        self.root.attributes('-topmost', False)  # Não fica sempre no topo, mas não minimiza
        
        # Inicializa log
        self.log("Aplicativo iniciado")
        self.log(f"PID do aplicativo: {self.current_pid}")
        
        # Garante que a janela seja restaurada se minimizada
        self.root.after(100, self.ensure_window_visible)
        
    def create_ui(self):
        # Título
        title_label = tk.Label(self.root, text="WhatsApp Rebooter", font=("Arial", 16, "bold"))
        title_label.pack(pady=15)
        
        # Frame para configuração do timer
        timer_frame = tk.LabelFrame(self.root, text="Configuração do Timer", padx=15, pady=15)
        timer_frame.pack(pady=15, padx=25, fill="x")
        
        # Horas
        hours_frame = tk.Frame(timer_frame)
        hours_frame.pack(pady=5)
        tk.Label(hours_frame, text="Horas:", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        self.hours_var = tk.StringVar(value="0")
        hours_spin = tk.Spinbox(hours_frame, from_=0, to=23, textvariable=self.hours_var, width=8)
        hours_spin.pack(side=tk.LEFT)
        
        # Minutos
        minutes_frame = tk.Frame(timer_frame)
        minutes_frame.pack(pady=5)
        tk.Label(minutes_frame, text="Minutos:", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        self.minutes_var = tk.StringVar(value="30")
        minutes_spin = tk.Spinbox(minutes_frame, from_=0, to=59, textvariable=self.minutes_var, width=8)
        minutes_spin.pack(side=tk.LEFT)
        
        # Segundos
        seconds_frame = tk.Frame(timer_frame)
        seconds_frame.pack(pady=5)
        tk.Label(seconds_frame, text="Segundos:", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        self.seconds_var = tk.StringVar(value="0")
        seconds_spin = tk.Spinbox(seconds_frame, from_=0, to=59, textvariable=self.seconds_var, width=8)
        seconds_spin.pack(side=tk.LEFT)
        
        # Status
        self.status_label = tk.Label(self.root, text="Status: Parado", fg="red", font=("Arial", 11, "bold"))
        self.status_label.pack(pady=10)
        
        # Próxima execução
        self.next_exec_label = tk.Label(self.root, text="Próxima execução: --", font=("Arial", 9))
        self.next_exec_label.pack(pady=5)
        
        # Botões
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=25, padx=20)
        
        self.start_button = tk.Button(button_frame, text="Iniciar", command=self.start_timer, 
                                      bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
                                      width=12, height=2, relief=tk.RAISED, cursor="hand2")
        self.start_button.pack(side=tk.LEFT, padx=8)
        
        self.stop_button = tk.Button(button_frame, text="Parar", command=self.stop_timer, 
                                     bg="#f44336", fg="white", font=("Arial", 10, "bold"), 
                                     width=12, height=2, state=tk.DISABLED, relief=tk.RAISED, cursor="hand2")
        self.stop_button.pack(side=tk.LEFT, padx=8)
        
        self.test_button = tk.Button(button_frame, text="Testar Agora", command=self.test_reboot, 
                                     bg="#2196F3", fg="white", font=("Arial", 10, "bold"), 
                                     width=12, height=2, relief=tk.RAISED, cursor="hand2")
        self.test_button.pack(side=tk.LEFT, padx=8)
        
        # Área de Log
        log_frame = tk.LabelFrame(self.root, text="Log de Atividades", padx=10, pady=10)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=80, 
                                                   font=("Consolas", 9), bg="#1e1e1e", 
                                                   fg="#d4d4d4", insertbackground="white")
        self.log_text.pack(fill="both", expand=True)
        
        # Botão para limpar log
        clear_log_btn = tk.Button(log_frame, text="Limpar Log", command=self.clear_log,
                                  bg="#666", fg="white", font=("Arial", 8))
        clear_log_btn.pack(pady=5)
    
    def log(self, message, level="INFO"):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Adiciona ao widget de texto
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Salva no arquivo
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Erro ao salvar log: {e}")
        
        # Também imprime no console
        print(log_entry.strip())
    
    def clear_log(self):
        """Limpa a área de log"""
        self.log_text.delete(1.0, tk.END)
        self.log("Log limpo pelo usuário")
        
    def find_whatsapp_window(self):
        """Encontra a janela do WhatsApp"""
        self.log("Procurando janela do WhatsApp...")
        
        try:
            app_hwnd = self.root.winfo_id()
            app_hwnd = win32gui.GetParent(app_hwnd) if win32gui.GetParent(app_hwnd) else app_hwnd
        except:
            app_hwnd = None
        
        def callback(hwnd, windows):
            if app_hwnd and hwnd == app_hwnd:
                return
            
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                
                if "Rebooter" in window_text or "rebooter" in window_text.lower():
                    return
                
                if "WhatsApp" in window_text and "Rebooter" not in window_text:
                    windows.append((hwnd, window_text))
                elif "whatsapp" in class_name.lower() and "rebooter" not in class_name.lower():
                    windows.append((hwnd, window_text))
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        if not windows:
            self.log("Nenhuma janela do WhatsApp encontrada", "WARNING")
        return windows
    
    def get_window_info(self, hwnd):
        """Obtém informações da janela (posição e dimensão)"""
        try:
            rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top
            
            # Verifica se a janela está minimizada
            placement = win32gui.GetWindowPlacement(hwnd)
            is_minimized = placement[1] == win32con.SW_SHOWMINIMIZED
            
            info = {
                'left': left,
                'top': top,
                'width': width,
                'height': height,
                'is_minimized': is_minimized
            }
            self.log(f"Informações da janela: Pos({left}, {top}) Tamanho({width}x{height}) Minimizada={is_minimized}")
            return info
        except Exception as e:
            self.log(f"Erro ao obter informações da janela: {e}", "ERROR")
            return None
    
    def save_window_info(self, window_info):
        """Salva informações da janela em arquivo JSON"""
        try:
            with open(self.window_info_file, 'w') as f:
                json.dump(window_info, f, indent=2)
            self.log(f"Informações salvas em {self.window_info_file}")
        except Exception as e:
            self.log(f"Erro ao salvar informações: {e}", "ERROR")
    
    def load_window_info(self):
        """Carrega informações da janela do arquivo JSON"""
        try:
            if os.path.exists(self.window_info_file):
                with open(self.window_info_file, 'r') as f:
                    info = json.load(f)
                self.log(f"Informações carregadas de {self.window_info_file}")
                return info
        except Exception as e:
            self.log(f"Erro ao carregar informações: {e}", "ERROR")
        return None
    
    def kill_whatsapp_process(self):
        """Encerra todos os processos do WhatsApp"""
        self.log("Procurando processos do WhatsApp...")
        killed = False
        
        whatsapp_process_names = ['whatsapp.exe', 'whatsappupdate.exe', 'whatsapp desktop.exe']
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['pid'] == self.current_pid:
                    continue
                
                proc_name = proc.info['name'].lower()
                if any(name in proc_name for name in whatsapp_process_names):
                    if 'rebooter' not in proc_name:
                        self.log(f"Encerrando processo: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.kill()
                        killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            except Exception as e:
                self.log(f"Erro ao encerrar processo: {e}", "ERROR")
        
        if not killed:
            self.log("Nenhum processo do WhatsApp foi encerrado", "WARNING")
        
        return killed
    
    def find_whatsapp_exe_path(self):
        """Tenta encontrar o caminho do executável do WhatsApp - PEGA DO PROCESSO EM EXECUÇÃO"""
        self.log("Procurando executável do WhatsApp em processos em execução...")
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['pid'] == self.current_pid:
                    continue
                proc_name = proc.info['name'].lower()
                if proc_name == 'whatsapp.exe':
                    exe_path = proc.info.get('exe')
                    if exe_path:
                        exe_path_lower = exe_path.lower()
                        exe_filename = os.path.basename(exe_path).lower()
                        if ('rebooter' not in exe_path_lower and 
                            'rebooter' not in exe_filename and
                            exe_filename == 'whatsapp.exe'):
                            self.log(f"Executável encontrado em processo: {exe_path}")
                            return exe_path
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        username = os.environ.get('USERNAME', '')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        programfiles = os.environ.get('PROGRAMFILES', '')
        programfilesx86 = os.environ.get('PROGRAMFILES(X86)', '')
        
        possible_paths = [
            os.path.join(localappdata, 'WhatsApp', 'WhatsApp.exe'),
            os.path.join(programfiles, 'WhatsApp', 'WhatsApp.exe'),
            os.path.join(programfilesx86, 'WhatsApp', 'WhatsApp.exe'),
            r'C:\Users\{}\AppData\Local\WhatsApp\WhatsApp.exe'.format(username),
            r'C:\Program Files\WhatsApp\WhatsApp.exe',
            r'C:\Program Files (x86)\WhatsApp\WhatsApp.exe',
        ]
        
        # Também procura em todos os drives
        for drive in ['C:', 'D:', 'E:', 'F:']:
            possible_paths.extend([
                os.path.join(drive, 'Users', username, 'AppData', 'Local', 'WhatsApp', 'WhatsApp.exe'),
                os.path.join(drive, 'Program Files', 'WhatsApp', 'WhatsApp.exe'),
                os.path.join(drive, 'Program Files (x86)', 'WhatsApp', 'WhatsApp.exe'),
            ])
        
        for path in possible_paths:
            if path and os.path.exists(path):
                self.log(f"Executável encontrado: {path}")
                return path
        
        # Tenta encontrar no registro do Windows
        try:
            import winreg
            self.log("Procurando no registro do Windows...")
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        try:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            if "WhatsApp" in display_name:
                                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                exe_path = os.path.join(install_location, "WhatsApp.exe")
                                if os.path.exists(exe_path):
                                    self.log(f"Executável encontrado no registro: {exe_path}")
                                    return exe_path
                        except:
                            pass
                        finally:
                            subkey.Close()
                    except:
                        pass
                key.Close()
            except:
                pass
        except ImportError:
            pass
        
        # Se não encontrar, usa o caminho especial do shell (como no PowerShell)
        # Isso funciona para UWP apps do Windows Store
        shell_path = "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"
        self.log(f"Usando caminho especial do shell: {shell_path}")
        return shell_path
    
    def restart_whatsapp(self, window_info, exe_path):
        """Reinicia o WhatsApp e restaura a posição/dimensão"""
        self.log(f"Iniciando WhatsApp: {exe_path}")
        
        # Se for caminho especial do shell (UWP app), usa os.startfile
        # Se for caminho normal, verifica se existe
        if exe_path.startswith("shell:"):
            try:
                os.startfile(exe_path)
                self.log("WhatsApp iniciado usando caminho especial do shell")
            except Exception as e:
                self.log(f"Erro ao iniciar WhatsApp: {e}", "ERROR")
                if not self.is_running:
                    messagebox.showerror("Erro", f"Não foi possível iniciar o WhatsApp: {e}")
                return False
        else:
            if not os.path.exists(exe_path):
                error_msg = f"Executável do WhatsApp não encontrado: {exe_path}"
                self.log(error_msg, "ERROR")
                if not self.is_running:
                    messagebox.showerror("Erro", error_msg)
                return False
            
            try:
                subprocess.Popen(exe_path, shell=True, 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                self.log("WhatsApp iniciado via subprocess")
            except Exception as e:
                self.log(f"Erro ao iniciar WhatsApp: {e}", "ERROR")
                if not self.is_running:
                    messagebox.showerror("Erro", f"Não foi possível iniciar o WhatsApp: {e}")
                return False
        
        time.sleep(1)
        
        self.log("Aguardando janela do WhatsApp aparecer...")
        max_attempts = 120
        attempt = 0
        hwnd = None
        
        while attempt < max_attempts:
            time.sleep(0.3)
            windows = self.find_whatsapp_window()
            if windows:
                hwnd = windows[0][0]
                self.log(f"Janela encontrada após {attempt * 0.3:.1f} segundo(s)")
                break
            attempt += 1
            if attempt % 20 == 0:
                self.log(f"Aguardando... ({attempt * 0.3:.0f}s)")
        
        if not hwnd:
            self.log("Janela do WhatsApp não foi encontrada", "ERROR")
            if not self.is_running:
                messagebox.showwarning("Aviso", "WhatsApp iniciado, mas a janela não foi encontrada.")
            return False
        
        time.sleep(0.3)
        
        if window_info:
            try:
                if window_info.get('is_minimized', False):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.1)
                
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOP,
                    window_info['left'],
                    window_info['top'],
                    window_info['width'],
                    window_info['height'],
                    win32con.SWP_SHOWWINDOW
                )
                
                time.sleep(0.1)
                rect = win32gui.GetWindowRect(hwnd)
                if rect[0] == window_info['left'] and rect[1] == window_info['top']:
                    self.log("Janela restaurada com sucesso")
                    return True
                else:
                    self.log("Janela restaurada, mas posição pode estar incorreta", "WARNING")
                    return True
            except Exception as e:
                self.log(f"Erro ao restaurar janela: {e}", "ERROR")
                return False
        
        return True
    
    def reboot_whatsapp(self):
        """Executa o processo completo de reboot do WhatsApp - retorna True se sucesso, False se falhou"""
        self.log("=" * 50)
        self.log("INICIANDO REBOOT DO WHATSAPP")
        self.log("=" * 50)
        
        # 1. Encontra a janela do WhatsApp
        windows = self.find_whatsapp_window()
        if not windows:
            error_msg = "WhatsApp não está aberto!"
            self.log(error_msg, "ERROR")
            if not self.is_running:
                messagebox.showwarning("Aviso", error_msg)
            return False
        
        hwnd = windows[0][0]
        window_title = windows[0][1]
        self.log(f"Janela encontrada: '{window_title}' (HWND: {hwnd})")
        
        # 2. PEGA O CAMINHO DO EXECUTÁVEL ANTES DE FECHAR (como no PowerShell)
        exe_path = self.find_whatsapp_exe_path()
        self.log(f"Caminho do executável obtido: {exe_path}")
        
        # 3. Salva informações da janela
        window_info = self.get_window_info(hwnd)
        if window_info:
            self.save_window_info(window_info)
        else:
            window_info = self.load_window_info()
            if not window_info:
                error_msg = "Não foi possível obter informações da janela!"
                self.log(error_msg, "ERROR")
                if not self.is_running:
                    messagebox.showwarning("Aviso", error_msg)
                return False
        
        # 4. Encerra o processo (como no PowerShell: Get-Process WhatsApp | Stop-Process)
        self.log("Encerrando processos do WhatsApp...")
        if not self.kill_whatsapp_process():
            error_msg = "Nenhum processo do WhatsApp foi encontrado para encerrar!"
            self.log(error_msg, "WARNING")
            if not self.is_running:
                messagebox.showwarning("Aviso", error_msg)
            return False
        
        # Aguarda processos encerrarem (como no PowerShell: Start-Sleep -Seconds 3)
        self.log("Aguardando processos encerrarem completamente...")
        time.sleep(3)
        
        # 5. Reinicia o WhatsApp usando o caminho obtido antes
        self.log("Reiniciando WhatsApp...")
        success = self.restart_whatsapp(window_info, exe_path)
        
        if success:
            self.log("=" * 50)
            self.log("REBOOT CONCLUÍDO COM SUCESSO!")
            self.log("=" * 50)
            return True
        else:
            self.log("=" * 50)
            self.log("REBOOT FALHOU!", "ERROR")
            self.log("=" * 50)
            return False
    
    def test_reboot(self):
        """Testa o reboot imediatamente"""
        if self.is_running:
            self.log("Timer está rodando, não é possível testar agora", "WARNING")
            messagebox.showinfo("Info", "Pare o timer antes de testar!")
            return
        self.log("Teste manual iniciado pelo usuário")
        self.reboot_whatsapp()
    
    def get_timer_seconds(self):
        """Calcula o total de segundos do timer"""
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            seconds = int(self.seconds_var.get())
            return hours * 3600 + minutes * 60 + seconds
        except:
            return 0
    
    def format_time(self, seconds):
        """Formata segundos em formato legível"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def timer_loop(self):
        """Loop principal do timer"""
        while self.is_running:
            total_seconds = self.get_timer_seconds()
            
            if total_seconds <= 0:
                self.root.after(0, lambda: messagebox.showwarning("Aviso", "Timer inválido! Configure um tempo maior que zero."))
                self.stop_timer()
                break
            
            # Atualiza o label de próxima execução
            self.root.after(0, lambda s=total_seconds: self.next_exec_label.config(
                text=f"Próxima execução em: {self.format_time(s)}"
            ))
            
            # Conta regressiva
            remaining = total_seconds
            while remaining > 0 and self.is_running:
                time.sleep(1)
                remaining -= 1
                self.root.after(0, lambda r=remaining: self.next_exec_label.config(
                    text=f"Próxima execução em: {self.format_time(r)}"
                ))
            
            if self.is_running:
                # Atualiza status para indicar que está executando
                self.root.after(0, lambda: self.status_label.config(
                    text="Status: Executando reboot...", fg="orange"
                ))
                self.root.after(0, lambda: self.next_exec_label.config(
                    text="Aguardando conclusão do reboot..."
                ))
                
                # Executa o reboot e aguarda a conclusão
                self.log("Timer disparado - executando reboot automático")
                success = self.reboot_whatsapp()
                
                if success:
                    self.log("Reboot concluído com sucesso, timer será reiniciado")
                else:
                    self.log("Reboot falhou, timer será reiniciado mesmo assim", "WARNING")
                
                # Restaura status normal
                if self.is_running:
                    self.root.after(0, lambda: self.status_label.config(
                        text="Status: Rodando", fg="green"
                    ))
                    self.root.after(0, lambda: self.next_exec_label.config(
                        text="Timer reiniciado, aguardando próxima execução..."
                    ))
                    
                    # Aguarda um pouco antes de reiniciar o timer
                    time.sleep(2)
                    self.log("Timer reiniciado, contagem regressiva iniciada")
    
    def start_timer(self):
        """Inicia o timer"""
        total_seconds = self.get_timer_seconds()
        if total_seconds <= 0:
            self.log("Tentativa de iniciar timer com valor inválido", "WARNING")
            messagebox.showwarning("Aviso", "Configure um timer válido (maior que zero)!")
            return
        
        self.log(f"Timer iniciado: {self.format_time(total_seconds)} ({total_seconds} segundos)")
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Rodando", fg="green")
        
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.timer_thread.start()
    
    def stop_timer(self):
        """Para o timer"""
        self.log("Timer parado pelo usuário")
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Parado", fg="red")
        self.next_exec_label.config(text="Próxima execução: --")
    
    def ensure_window_visible(self):
        """Garante que a janela do aplicativo esteja visível"""
        try:
            # Obtém o handle da janela do tkinter
            hwnd = self.root.winfo_id()
            # Converte para handle do Windows
            hwnd = win32gui.GetParent(hwnd) if win32gui.GetParent(hwnd) else hwnd
            
            # Verifica se está minimizada e restaura
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                self.log("Janela do aplicativo restaurada (estava minimizada)")
        except Exception as e:
            # Ignora erros silenciosamente
            pass
    
    def on_closing(self):
        """Gerencia o fechamento da janela"""
        if self.is_running:
            if messagebox.askokcancel("Sair", "O timer está rodando. Deseja realmente sair?"):
                self.is_running = False
                self.log("Aplicativo fechado pelo usuário")
                self.root.destroy()
        else:
            self.log("Aplicativo fechado pelo usuário")
            self.root.destroy()

def main():
    root = tk.Tk()
    app = WhatsAppRebooter(root)
    root.mainloop()

if __name__ == "__main__":
    main()

