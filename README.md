# WhatsApp Rebooter

Aplicativo profissional para Windows que reinicia automaticamente o WhatsApp Desktop mantendo a posição e dimensão da janela.

## 🎯 Funcionalidades

- ✅ Captura automática da posição e dimensão da janela do WhatsApp
- ✅ Encerramento seguro de processos do WhatsApp
- ✅ Reinício automático do WhatsApp
- ✅ Restauração precisa da janela na mesma posição e dimensão
- ✅ Timer configurável (horas, minutos, segundos)
- ✅ Interface gráfica moderna e intuitiva
- ✅ Botão de teste para reiniciar imediatamente
- ✅ Sistema de logging detalhado com diagnóstico passo a passo
- ✅ Arquitetura modular e profissional

## 📋 Requisitos

- Windows 10/11
- Python 3.7 ou superior
- WhatsApp Desktop instalado

## 🚀 Instalação

1. Clone ou baixe o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 💻 Como Usar

### Opção 1: Executar diretamente com Python

```bash
python main.py
```

### Opção 2: Gerar executável (.exe)

**Windows:**
```bash
build.bat
```

**Linux/WSL (para gerar .exe do Windows):**
```bash
chmod +x build.sh
./build.sh
```

O executável será criado na pasta `instalador/WhatsAppRebooter.exe`

## 📖 Uso do Aplicativo

1. Abra o WhatsApp Desktop normalmente
2. Execute o WhatsApp Rebooter (`python main.py` ou o executável)
3. Configure o timer (horas, minutos, segundos) - exemplo: 0 horas, 30 minutos, 0 segundos
4. Clique em "Iniciar" para começar o timer automático
5. Use "Testar Agora" para reiniciar o WhatsApp imediatamente (sem esperar o timer)
6. Use "Parar" para interromper o timer

## 🏗️ Arquitetura

O projeto foi organizado de forma profissional e modular:

```
whatapp-rebooter/
├── main.py                 # Ponto de entrada principal
├── src/
│   ├── core/              # Lógica de negócio
│   │   ├── reboot_service.py    # Serviço de reboot
│   │   └── timer_service.py     # Serviço de timer
│   ├── ui/                # Interface gráfica
│   │   └── main_window.py       # Janela principal
│   ├── process_manager/   # Gerenciamento de processos
│   │   ├── window_manager.py    # Gerenciamento de janelas
│   │   └── process_manager.py   # Gerenciamento de processos
│   └── utils/             # Utilitários
│       ├── logger.py            # Sistema de logging
│       └── config.py            # Gerenciamento de configurações
├── logs/                  # Logs da aplicação
├── config.json            # Configurações (gerado automaticamente)
└── whatsapp_window_info.json  # Informações da janela (gerado automaticamente)
```

### Componentes Principais

- **RebootService**: Orquestra o processo completo de reboot em 7 passos claros
- **TimerService**: Gerencia o timer com callbacks e atualizações de status
- **WindowManager**: Detecta e gerencia janelas do Windows
- **ProcessManager**: Encontra, encerra e inicia processos do WhatsApp
- **Logger**: Sistema de logging centralizado com níveis e arquivos
- **Config**: Gerenciamento de configurações persistente

## 🔍 Como Funciona

O processo de reboot é executado em 7 passos claros e diagnosticáveis:

1. **DETECÇÃO DE JANELA**: Procura e identifica a janela do WhatsApp
2. **OBTENÇÃO DO CAMINHO**: Encontra o executável do WhatsApp
3. **CAPTURA DE INFORMAÇÕES**: Salva posição, tamanho e estado da janela
4. **ENCERRAMENTO DE PROCESSOS**: Encerra todos os processos do WhatsApp
5. **REINÍCIO DO WHATSAPP**: Inicia o WhatsApp novamente
6. **RESTAURAÇÃO DA JANELA**: Restaura posição e tamanho salvos
7. **CONCLUÍDO**: Verifica sucesso e registra no log

Cada passo é registrado detalhadamente no log para facilitar diagnóstico.

## 📝 Logs

Os logs são salvos automaticamente em:
- **Arquivo**: `logs/whatsapp_rebooter_YYYYMMDD.log`
- **Interface**: Área de log na aplicação
- **Console**: Saída padrão

Cada operação é registrada com timestamp, nível e mensagem detalhada.

## ⚙️ Configurações

O arquivo `config.json` é criado automaticamente na primeira execução e contém:

```json
{
  "window_info_file": "whatsapp_window_info.json",
  "whatsapp_process_names": [
    "whatsapp.exe",
    "whatsappupdate.exe",
    "whatsapp desktop.exe"
  ],
  "window_restore_timeout": 120,
  "process_kill_wait_time": 3,
  "window_detection_interval": 0.3
}
```

## 🐛 Solução de Problemas

### Erro: "WhatsApp não está aberto!"
- Certifique-se de que o WhatsApp Desktop está aberto antes de iniciar o timer
- Verifique o log para mais detalhes

### Erro: "Não foi possível iniciar o WhatsApp"
- Verifique se o WhatsApp está instalado
- O aplicativo procura em múltiplos locais automaticamente
- Verifique o log para ver onde procurou

### A janela não é restaurada corretamente
- Certifique-se de que o WhatsApp estava aberto quando você iniciou o timer pela primeira vez
- Tente usar "Testar Agora" para verificar se funciona
- Verifique o log para ver se houve erros na restauração

### Timer não funciona
- Verifique se configurou valores maiores que zero
- Verifique o log para mensagens de erro
- Certifique-se de que o timer está rodando (status verde)

## 🔧 Desenvolvimento

### Estrutura de Código

O código foi organizado seguindo princípios de:
- **Separação de Responsabilidades**: Cada módulo tem uma responsabilidade única
- **Baixo Acoplamento**: Módulos se comunicam através de interfaces claras
- **Alta Coesão**: Funcionalidades relacionadas estão agrupadas
- **Facilidade de Diagnóstico**: Cada passo é registrado e pode ser rastreado

### Adicionando Novas Funcionalidades

1. **Nova funcionalidade de processo**: Adicione em `src/process_manager/`
2. **Nova funcionalidade de UI**: Adicione em `src/ui/`
3. **Nova lógica de negócio**: Adicione em `src/core/`
4. **Novos utilitários**: Adicione em `src/utils/`

## 📄 Licença

Este projeto é fornecido "como está", sem garantias.
