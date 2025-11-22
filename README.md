# WhatsApp Rebooter

Aplicativo simples para Windows que reinicia automaticamente o WhatsApp Desktop mantendo a posição e dimensão da janela.

## Funcionalidades

- ✅ Captura a posição e dimensão da janela do WhatsApp
- ✅ Encerra o processo do WhatsApp
- ✅ Reinicia o WhatsApp automaticamente
- ✅ Restaura a janela na mesma posição e dimensão anteriores
- ✅ Timer configurável (horas, minutos, segundos)
- ✅ Interface gráfica simples e intuitiva
- ✅ Botão de teste para reiniciar imediatamente

## Requisitos

- Windows (testado no Windows 10/11)
- Python 3.7 ou superior
- WhatsApp Desktop instalado

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como Usar

### Opção 1: Executar diretamente com Python

```bash
python whatsapp_rebooter.py
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

## Uso do Aplicativo

1. Abra o WhatsApp Desktop normalmente
2. Execute o WhatsApp Rebooter
3. Configure o timer (horas, minutos, segundos) - exemplo: 0 horas, 30 minutos, 0 segundos
4. Clique em "Iniciar" para começar o timer automático
5. Use "Testar Agora" para reiniciar o WhatsApp imediatamente (sem esperar o timer)
6. Use "Parar" para interromper o timer

## Como Funciona

1. O aplicativo detecta a janela do WhatsApp Desktop
2. Salva a posição (X, Y) e dimensões (largura, altura) da janela
3. Encerra todos os processos relacionados ao WhatsApp
4. Reinicia o WhatsApp
5. Restaura a janela na mesma posição e dimensão anteriores
6. Repete o processo de acordo com o timer configurado

## Notas

- O aplicativo salva as informações da janela em `whatsapp_window_info.json`
- Se o WhatsApp não estiver aberto quando o timer disparar, o aplicativo mostrará um aviso
- O aplicativo tenta encontrar o WhatsApp em locais comuns, mas se não encontrar, tentará usar o comando do sistema

## Solução de Problemas

**Erro: "WhatsApp não está aberto!"**
- Certifique-se de que o WhatsApp Desktop está aberto antes de iniciar o timer

**Erro: "Não foi possível iniciar o WhatsApp"**
- Verifique se o WhatsApp está instalado
- O aplicativo procura em: `%LOCALAPPDATA%\WhatsApp\WhatsApp.exe`

**A janela não é restaurada corretamente**
- Certifique-se de que o WhatsApp estava aberto quando você iniciou o timer pela primeira vez
- Tente usar "Testar Agora" para verificar se funciona

## Licença

Este projeto é fornecido "como está", sem garantias.

