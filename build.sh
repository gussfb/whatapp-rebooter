#!/bin/bash

# Muda para o diretório onde o script está localizado
cd "$(dirname "$0")"

echo "Diretório atual: $(pwd)"
echo ""

# Cria a pasta de output ANTES de tudo
if [ ! -d "instalador" ]; then
    echo "Criando pasta instalador..."
    mkdir -p instalador
    echo "Pasta instalador criada!"
else
    echo "Pasta instalador já existe."
fi
echo ""

echo "Instalando dependências..."
pip install -r requirements.txt
pip install pyinstaller

echo ""
echo "Criando executável..."
echo ""

# Verifica se o diretorio src existe
if [ ! -d "src" ]; then
    echo "ERRO: Diretório src não encontrado!"
    exit 1
fi

# Executa o PyInstaller e define a pasta de output
# Usa --paths para adicionar src ao PYTHONPATH (melhor que --add-data para módulos Python)
# --collect-submodules coleta todos os submódulos automaticamente
pyinstaller --onefile --windowed --name "WhatsAppRebooter" --icon=NONE --distpath "instalador" --workpath "instalador/build" --specpath "instalador" --paths "." --collect-submodules src --hidden-import win32timezone main.py

echo ""
echo "========================================"
if [ -f "instalador/WhatsAppRebooter.exe" ]; then
    echo "SUCESSO! Executável criado em:"
    echo "$(pwd)/instalador/WhatsAppRebooter.exe"
else
    echo "ERRO: Executável não foi criado!"
    echo "Verifique as mensagens de erro acima."
fi
echo "========================================"

