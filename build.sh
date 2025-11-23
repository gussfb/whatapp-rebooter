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

# Verifica se existe ícone (usa caminho absoluto para evitar problemas)
ICON_PARAM=""
if [ -f "assets/icon.ico" ]; then
    # Usa caminho absoluto para garantir que funcione mesmo com --specpath
    ICON_PATH="$(cd "$(dirname "$0")" && pwd)/assets/icon.ico"
    ICON_PARAM="--icon=\"$ICON_PATH\""
    echo "Ícone encontrado: $ICON_PATH"
else
    echo "Aviso: Ícone não encontrado. Usando padrão do Windows."
fi

# Executa o PyInstaller e define a pasta de output
# Usa --paths para adicionar src ao PYTHONPATH (melhor que --add-data para módulos Python)
# --collect-submodules coleta todos os submódulos automaticamente
if [ -n "$ICON_PARAM" ]; then
    pyinstaller --onefile --windowed --name "WhatsAppRebooter" $ICON_PARAM --distpath "instalador" --workpath "instalador/build" --specpath "instalador" --paths "." --collect-submodules src --hidden-import win32timezone main.py
else
    pyinstaller --onefile --windowed --name "WhatsAppRebooter" --distpath "instalador" --workpath "instalador/build" --specpath "instalador" --paths "." --collect-submodules src --hidden-import win32timezone main.py
fi

# Copia pasta assets para instalador (para ícones e recursos)
if [ -d "assets" ]; then
    echo ""
    echo "Copiando pasta assets para instalador..."
    if [ -d "instalador/assets" ]; then
        rm -rf "instalador/assets"
    fi
    cp -r "assets" "instalador/assets"
    echo "Pasta assets copiada com sucesso!"
else
    echo ""
    echo "Aviso: Pasta assets não encontrada."
fi

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

