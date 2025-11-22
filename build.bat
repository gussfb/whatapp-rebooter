@echo off
REM Muda para o diretório onde o script está localizado
cd /d "%~dp0"

echo Diretorio atual: %CD%
echo.

REM Cria a pasta de output ANTES de tudo
if not exist "instalador" (
    echo Criando pasta instalador...
    mkdir instalador
    echo Pasta instalador criada!
) else (
    echo Pasta instalador ja existe.
)
echo.

echo Instalando dependencias...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Criando executavel...
echo.

REM Verifica se o diretorio src existe
if not exist "src" (
    echo ERRO: Diretorio src nao encontrado!
    pause
    exit /b 1
)

REM Executa o PyInstaller e define a pasta de output
REM Usa --paths para adicionar src ao PYTHONPATH (melhor que --add-data para modulos Python)
REM --collect-submodules coleta todos os submódulos automaticamente
pyinstaller --onefile --windowed --name "WhatsAppRebooter" --icon=NONE --distpath "instalador" --workpath "instalador\build" --specpath "instalador" --paths "." --collect-submodules src --hidden-import win32timezone main.py

echo.
echo ========================================
if exist "instalador\WhatsAppRebooter.exe" (
    echo SUCESSO! Executavel criado em:
    echo %CD%\instalador\WhatsAppRebooter.exe
) else (
    echo ERRO: Executavel nao foi criado!
    echo Verifique as mensagens de erro acima.
)
echo ========================================
echo.
echo Pressione qualquer tecla para abrir a pasta instalador...
pause >nul
if exist "instalador" (
    explorer instalador
)

