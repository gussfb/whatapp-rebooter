"""Gerenciamento de processos do Windows."""

import os
import subprocess
import time
from typing import Optional, List

import psutil
import winreg

from src.utils.logger import Logger


class ProcessManager:
    """Gerencia processos do WhatsApp."""
    
    def __init__(self, logger: Logger, config):
        """
        Inicializa o gerenciador de processos.
        
        Args:
            logger: Instância do logger
            config: Instância de configurações
        """
        self.logger = logger
        self.config = config
        self.current_pid = os.getpid()
        self.process_names = config.get_process_names()
    
    def find_whatsapp_processes(self) -> List[psutil.Process]:
        """
        Encontra todos os processos do WhatsApp em execução.
        
        Returns:
            Lista de processos do WhatsApp
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['pid'] == self.current_pid:
                    continue
                
                proc_name = proc.info['name'].lower()
                if any(name in proc_name for name in self.process_names):
                    if 'rebooter' not in proc_name:
                        processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            except Exception as e:
                self.logger.debug(f"Erro ao verificar processo: {e}")
        
        return processes
    
    def kill_whatsapp_processes(self) -> bool:
        """
        Encerra todos os processos do WhatsApp.
        
        Returns:
            True se pelo menos um processo foi encerrado, False caso contrário
        """
        self.logger.info("Procurando processos do WhatsApp...")
        processes = self.find_whatsapp_processes()
        
        if not processes:
            self.logger.warning("Nenhum processo do WhatsApp encontrado")
            return False
        
        killed = False
        for proc in processes:
            try:
                self.logger.info(f"Encerrando processo: {proc.name()} (PID: {proc.pid})")
                proc.kill()
                killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.logger.debug(f"Erro ao encerrar processo {proc.pid}: {e}")
            except Exception as e:
                self.logger.error(f"Erro ao encerrar processo {proc.pid}: {e}", exc_info=True)
        
        if killed:
            self.logger.info(f"{len(processes)} processo(s) encerrado(s)")
        
        return killed
    
    def wait_for_processes_to_end(self, timeout: int = 10):
        """
        Aguarda processos encerrarem completamente monitorando a árvore de processos.
        
        Args:
            timeout: Tempo máximo de espera em segundos
        """
        self.logger.info("Aguardando processos encerrarem completamente...")
        
        max_wait = timeout
        check_interval = 0.2  # Verifica a cada 200ms
        elapsed = 0
        
        while elapsed < max_wait:
            processes = self.find_whatsapp_processes()
            if not processes:
                self.logger.info(f"Todos os processos foram encerrados (após {elapsed:.1f}s)")
                return
            
            time.sleep(check_interval)
            elapsed += check_interval
            
            # Log a cada segundo
            if int(elapsed) != int(elapsed - check_interval):
                remaining = len(processes)
                self.logger.debug(f"Processos ainda ativos: {remaining} (após {elapsed:.1f}s)")
        
        # Se chegou aqui, timeout atingido
        remaining = self.find_whatsapp_processes()
        if remaining:
            self.logger.warning(f"Timeout atingido. {len(remaining)} processo(s) ainda ativo(s)")
        else:
            self.logger.info(f"Todos os processos foram encerrados (após {elapsed:.1f}s)")
    
    def find_whatsapp_exe_path(self) -> Optional[str]:
        """
        Encontra o caminho do executável do WhatsApp.
        
        Returns:
            Caminho do executável ou None
        """
        self.logger.info("Procurando executável do WhatsApp...")
        
        # 1. Tenta obter do processo em execução
        exe_path = self._find_from_running_process()
        if exe_path:
            return exe_path
        
        # 2. Tenta locais comuns
        exe_path = self._find_in_common_locations()
        if exe_path:
            return exe_path
        
        # 3. Tenta registro do Windows
        exe_path = self._find_in_registry()
        if exe_path:
            return exe_path
        
        # 4. Usa caminho especial do shell (UWP app)
        shell_path = "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"
        self.logger.info(f"Usando caminho especial do shell: {shell_path}")
        return shell_path
    
    def _find_from_running_process(self) -> Optional[str]:
        """Tenta encontrar executável em processos em execução."""
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['pid'] == self.current_pid:
                    continue
                
                proc_name = proc.info['name'].lower()
                if proc_name == 'whatsapp.exe':
                    exe_path = proc.info.get('exe')
                    if exe_path and os.path.exists(exe_path):
                        exe_filename = os.path.basename(exe_path).lower()
                        if 'rebooter' not in exe_path.lower() and exe_filename == 'whatsapp.exe':
                            self.logger.info(f"Executável encontrado em processo: {exe_path}")
                            return exe_path
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return None
    
    def _find_in_common_locations(self) -> Optional[str]:
        """Procura em locais comuns de instalação."""
        username = os.environ.get('USERNAME', '')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        programfiles = os.environ.get('PROGRAMFILES', '')
        programfilesx86 = os.environ.get('PROGRAMFILES(X86)', '')
        
        possible_paths = [
            os.path.join(localappdata, 'WhatsApp', 'WhatsApp.exe'),
            os.path.join(programfiles, 'WhatsApp', 'WhatsApp.exe'),
            os.path.join(programfilesx86, 'WhatsApp', 'WhatsApp.exe'),
        ]
        
        # Procura em drives comuns
        for drive in ['C:', 'D:', 'E:', 'F:']:
            possible_paths.extend([
                os.path.join(drive, 'Users', username, 'AppData', 'Local', 'WhatsApp', 'WhatsApp.exe'),
                os.path.join(drive, 'Program Files', 'WhatsApp', 'WhatsApp.exe'),
                os.path.join(drive, 'Program Files (x86)', 'WhatsApp', 'WhatsApp.exe'),
            ])
        
        for path in possible_paths:
            if path and os.path.exists(path):
                self.logger.info(f"Executável encontrado: {path}")
                return path
        
        return None
    
    def _find_in_registry(self) -> Optional[str]:
        """Procura no registro do Windows."""
        try:
            self.logger.debug("Procurando no registro do Windows...")
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
            )
            
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
                                self.logger.info(f"Executável encontrado no registro: {exe_path}")
                                return exe_path
                    except (FileNotFoundError, OSError):
                        pass
                    finally:
                        subkey.Close()
                except (FileNotFoundError, OSError):
                    pass
            
            key.Close()
        except Exception as e:
            self.logger.debug(f"Erro ao procurar no registro: {e}")
        
        return None
    
    def start_whatsapp(self, exe_path: str) -> bool:
        """
        Inicia o WhatsApp.
        
        Args:
            exe_path: Caminho do executável
            
        Returns:
            True se iniciado com sucesso, False caso contrário
        """
        self.logger.info(f"Iniciando WhatsApp: {exe_path}")
        
        # Caminho especial do shell (UWP app)
        if exe_path.startswith("shell:"):
            try:
                os.startfile(exe_path)
                self.logger.info("WhatsApp iniciado usando caminho especial do shell")
                return True
            except Exception as e:
                self.logger.error(f"Erro ao iniciar WhatsApp: {e}", exc_info=True)
                return False
        
        # Caminho normal
        if not os.path.exists(exe_path):
            self.logger.error(f"Executável não encontrado: {exe_path}")
            return False
        
        try:
            subprocess.Popen(
                exe_path,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.logger.info("WhatsApp iniciado via subprocess")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao iniciar WhatsApp: {e}", exc_info=True)
            return False

