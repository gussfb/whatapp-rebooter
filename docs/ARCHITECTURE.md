# Arquitetura do WhatsApp Rebooter

## Visão Geral

O projeto foi arquitetado seguindo princípios de **Clean Architecture** e **Separation of Concerns**, garantindo código modular, testável e fácil de manter.

## Estrutura de Diretórios

```
whatapp-rebooter/
├── main.py                          # Ponto de entrada - orquestra todos os componentes
├── src/
│   ├── __init__.py                  # Package marker
│   ├── core/                        # Lógica de negócio (Business Logic)
│   │   ├── __init__.py
│   │   ├── reboot_service.py        # Orquestra o processo de reboot
│   │   └── timer_service.py         # Gerencia timer e execução periódica
│   ├── ui/                          # Camada de apresentação (Presentation Layer)
│   │   ├── __init__.py
│   │   └── main_window.py           # Interface gráfica Tkinter
│   ├── process_manager/             # Camada de infraestrutura (Infrastructure Layer)
│   │   ├── __init__.py
│   │   ├── window_manager.py        # Gerenciamento de janelas Windows
│   │   └── process_manager.py       # Gerenciamento de processos Windows
│   └── utils/                       # Utilitários compartilhados
│       ├── __init__.py
│       ├── logger.py                # Sistema de logging centralizado
│       └── config.py                # Gerenciamento de configurações/
├── logs/                            # Logs da aplicação (gerado automaticamente)
├── config.json                      # Configurações (gerado automaticamente)
└── whatsapp_window_info.json        # Estado da janela (gerado automaticamente)
```

## Camadas da Arquitetura

### 1. Camada de Apresentação (`src/ui/`)

**Responsabilidade**: Interface com o usuário

- **MainWindow**: Gerencia a interface gráfica Tkinter
  - Cria e gerencia widgets
  - Conecta eventos de UI com serviços
  - Atualiza status e logs na interface

### 2. Camada de Negócio (`src/core/`)

**Responsabilidade**: Lógica de negócio e orquestração

- **RebootService**: Orquestra o processo completo de reboot
  - Executa 7 passos claros e diagnosticáveis
  - Coordena WindowManager e ProcessManager
  - Retorna status de sucesso/falha
  
- **TimerService**: Gerencia execução periódica
  - Contagem regressiva
  - Callbacks para atualização de UI
  - Thread separada para não bloquear UI

### 3. Camada de Infraestrutura (`src/process_manager/`)

**Responsabilidade**: Interação com sistema operacional

- **WindowManager**: Gerencia janelas do Windows
  - Detecta janelas do WhatsApp
  - Captura e restaura posição/tamanho
  - Salva/carrega estado da janela
  
- **ProcessManager**: Gerencia processos do Windows
  - Encontra processos do WhatsApp
  - Encerra processos
  - Inicia WhatsApp
  - Localiza executável

### 4. Utilitários (`src/utils/`)

**Responsabilidade**: Serviços compartilhados

- **Logger**: Sistema de logging
  - Múltiplos handlers (arquivo, console)
  - Níveis de log (DEBUG, INFO, WARNING, ERROR)
  - Formatação de passos de execução
  
- **Config**: Gerenciamento de configurações
  - Carrega/salva JSON
  - Valores padrão
  - Acesso tipado

## Fluxo de Execução

### Inicialização

```
main.py
  ├── Cria Config
  ├── Cria Logger
  ├── Cria WindowManager
  ├── Cria ProcessManager
  ├── Cria RebootService (usa WindowManager + ProcessManager)
  ├── Cria TimerService (usa RebootService.execute_reboot)
  ├── Cria MainWindow (usa RebootService + TimerService)
  └── Inicia loop Tkinter
```

### Execução de Reboot

```
RebootService.execute_reboot()
  ├── PASSO 1: WindowManager.find_whatsapp_windows()
  ├── PASSO 2: ProcessManager.find_whatsapp_exe_path()
  ├── PASSO 3: WindowManager.get_window_info() + save_window_info()
  ├── PASSO 4: ProcessManager.kill_whatsapp_processes()
  ├── PASSO 5: ProcessManager.start_whatsapp()
  ├── PASSO 6: WindowManager.wait_for_window() + restore_window()
  └── PASSO 7: Concluído
```

### Timer Automático

```
TimerService.start()
  └── Thread separada:
      ├── Loop de contagem regressiva
      ├── Atualiza UI via callbacks
      ├── Chama RebootService.execute_reboot()
      └── Reinicia loop
```

## Princípios de Design

### 1. Separação de Responsabilidades

Cada classe tem uma única responsabilidade:
- `WindowManager` → Apenas janelas
- `ProcessManager` → Apenas processos
- `RebootService` → Apenas orquestração
- `TimerService` → Apenas timer

### 2. Inversão de Dependências

Camadas superiores dependem de abstrações:
- `RebootService` recebe `WindowManager` e `ProcessManager` via construtor
- `MainWindow` recebe serviços via construtor
- Facilita testes e substituição de implementações

### 3. Facilidade de Diagnóstico

Cada passo é claramente identificado:
- Logs estruturados com `logger.step()`
- Mensagens descritivas
- Tratamento de erros em cada etapa

### 4. Baixo Acoplamento

Módulos se comunicam através de interfaces claras:
- Métodos bem definidos
- Tipos de retorno explícitos
- Sem dependências circulares

### 5. Alta Coesão

Funcionalidades relacionadas estão agrupadas:
- Tudo relacionado a janelas em `WindowManager`
- Tudo relacionado a processos em `ProcessManager`
- Tudo relacionado a UI em `MainWindow`

## Extensibilidade

### Adicionar Nova Funcionalidade

1. **Nova funcionalidade de sistema**: Adicione em `src/process_manager/`
2. **Nova funcionalidade de UI**: Adicione em `src/ui/`
3. **Nova lógica de negócio**: Adicione em `src/core/`
4. **Novo utilitário**: Adicione em `src/utils/`

### Exemplo: Adicionar suporte a Telegram

1. Criar `src/process_manager/telegram_manager.py`
2. Adicionar método em `RebootService` ou criar `TelegramRebootService`
3. Integrar na UI se necessário

## Testabilidade

A arquitetura facilita testes:

- **Unit Tests**: Cada módulo pode ser testado isoladamente
- **Integration Tests**: Serviços podem ser testados com mocks
- **E2E Tests**: Fluxo completo pode ser testado

### Exemplo de Teste

```python
# Mock dos componentes
mock_window_manager = Mock(WindowManager)
mock_process_manager = Mock(ProcessManager)
logger = Logger()

# Testa serviço isoladamente
service = RebootService(logger, mock_window_manager, mock_process_manager)
result = service.execute_reboot()
assert result == True
```

## Logging e Diagnóstico

### Níveis de Log

- **DEBUG**: Informações detalhadas para desenvolvimento
- **INFO**: Informações gerais de execução
- **WARNING**: Situações que podem causar problemas
- **ERROR**: Erros que impedem execução
- **STEP**: Formatação especial para passos de execução

### Formato de Logs

```
[2024-01-15 10:30:45] [INFO] Aplicativo iniciado
============================================================
PASSO 1: DETECÇÃO DE JANELA
  → Procurando janela do WhatsApp...
============================================================
[2024-01-15 10:30:45] [INFO] Janela encontrada: 'WhatsApp' (HWND: 123456)
```

## Configuração

Configurações são centralizadas em `Config`:
- Valores padrão definidos
- Persistência em JSON
- Acesso tipado e seguro
- Fácil de estender

## Conclusão

Esta arquitetura garante:
- ✅ Código limpo e organizado
- ✅ Fácil manutenção
- ✅ Fácil extensão
- ✅ Fácil teste
- ✅ Fácil diagnóstico
- ✅ Baixo acoplamento
- ✅ Alta coesão

