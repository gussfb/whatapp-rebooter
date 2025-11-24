"""Gerenciamento de configurações."""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any


class Config:
    """Gerenciador de configurações do aplicativo."""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_file: Nome do arquivo de configuração
        """
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._load()
    
    def _load(self):
        """Carrega configurações do arquivo."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except json.JSONDecodeError as e:
                print(f"[Config] Aviso: Arquivo de config com JSON inválido ({e}), usando configurações padrão")
                self._config = self._get_default_config()
            except (OSError, IOError) as e:
                print(f"[Config] Aviso: Erro ao ler arquivo de config ({e}), usando configurações padrão")
                self._config = self._get_default_config()
        else:
            self._config = self._get_default_config()
            self._save()
    
    def _save(self):
        """Salva configurações no arquivo."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except (OSError, IOError) as e:
            print(f"[Config] Erro: Falha ao salvar configurações ({e})")
        except TypeError as e:
            print(f"[Config] Erro: Dados de configuração inválidos para serialização ({e})")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configurações padrão."""
        return {
            "window_info_file": "whatsapp_window_info.json",
            "whatsapp_process_names": [
                "whatsapp.exe",
                "whatsappupdate.exe",
                "whatsapp desktop.exe"
            ],
            "window_restore_timeout": 120,
            "process_kill_wait_time": 3,
            "window_detection_interval": 0.3,
            "user_settings": {
                "timer_hours": 4,
                "timer_minutes": 0,
                "timer_seconds": 0,
                "auto_start_on_detection": True
            }
        }
    
    def get_user_settings(self) -> Dict[str, Any]:
        """Retorna configurações do usuário."""
        return self.get("user_settings", {
            "timer_hours": 4,
            "timer_minutes": 0,
            "timer_seconds": 0,
            "auto_start_on_detection": True
        })
    
    def save_user_settings(self, hours: int, minutes: int, seconds: int, auto_start: bool = True):
        """
        Salva configurações do usuário.
        
        Args:
            hours: Horas do timer
            minutes: Minutos do timer
            seconds: Segundos do timer
            auto_start: Se deve iniciar automaticamente ao detectar WhatsApp
        """
        if "user_settings" not in self._config:
            self._config["user_settings"] = {}
        
        self._config["user_settings"].update({
            "timer_hours": hours,
            "timer_minutes": minutes,
            "timer_seconds": seconds,
            "auto_start_on_detection": auto_start
        })
        self._save()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração.
        
        Args:
            key: Chave da configuração
            default: Valor padrão se não encontrado
            
        Returns:
            Valor da configuração ou default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Define valor de configuração.
        
        Args:
            key: Chave da configuração
            value: Valor a ser definido
        """
        self._config[key] = value
        self._save()
    
    def get_window_info_file(self) -> str:
        """Retorna o caminho do arquivo de informações da janela."""
        return self.get("window_info_file", "whatsapp_window_info.json")
    
    def get_process_names(self) -> list:
        """Retorna lista de nomes de processos do WhatsApp."""
        return self.get("whatsapp_process_names", ["whatsapp.exe"])

