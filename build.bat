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

REM Executa o PyInstaller e define a pasta de output
pyinstaller --onefile --windowed --name "WhatsAppRebooter" --icon=NONE --distpath "instalador" --workpath "instalador\build" --specpath "instalador" whatsapp_rebooter.py

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

