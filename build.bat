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

REM Limpa arquivo .spec antigo se existir (pode ter configurações incorretas)
if exist "instalador\WhatsAppRebooter.spec" (
    echo Limpando arquivo .spec antigo...
    del "instalador\WhatsAppRebooter.spec"
)

REM Verifica se o executável está aberto (pode causar erro de permissão)
tasklist /FI "IMAGENAME eq WhatsAppRebooter.exe" 2>NUL | find /I /N "WhatsAppRebooter.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo AVISO: WhatsAppRebooter.exe esta em execucao!
    echo Feche o aplicativo antes de compilar novamente.
    pause
    exit /b 1
)

REM Verifica se existe ícone (usa caminho relativo simples)
set ICON_PARAM=
set USE_ICON=0
if exist "assets\icon.ico" (
    REM Verifica se o arquivo é acessível (não está bloqueado)
    type "assets\icon.ico" >nul 2>&1
    if not errorlevel 1 (
        REM Usa caminho relativo simples (PyInstaller resolve melhor)
        set ICON_PARAM=--icon=assets\icon.ico
        set USE_ICON=1
        echo Icone encontrado: assets\icon.ico
    ) else (
        echo AVISO: Icone existe mas nao esta acessivel (pode estar bloqueado)
        echo Continuando sem icone...
    )
) else (
    echo Aviso: Icone nao encontrado em assets\icon.ico
    echo Continuando sem icone...
)

REM Executa o PyInstaller
REM Usa caminho relativo para o ícone (mais confiável)
if "%USE_ICON%"=="1" (
    echo Executando PyInstaller com icone...
    pyinstaller --clean --onefile --windowed --name "WhatsAppRebooter" --icon=assets\icon.ico --distpath "instalador" --workpath "instalador\build" --paths "." --collect-submodules src --hidden-import win32timezone main.py
) else (
    echo Executando PyInstaller sem icone...
    pyinstaller --clean --onefile --windowed --name "WhatsAppRebooter" --distpath "instalador" --workpath "instalador\build" --paths "." --collect-submodules src --hidden-import win32timezone main.py
)

REM Move o arquivo .spec para a pasta instalador se foi gerado na raiz
if exist "WhatsAppRebooter.spec" (
    if not exist "instalador\WhatsAppRebooter.spec" (
        move "WhatsAppRebooter.spec" "instalador\WhatsAppRebooter.spec" >nul
    ) else (
        del "WhatsAppRebooter.spec"
    )
)

REM Copia pasta assets para instalador (para ícones e recursos)
if exist "assets" (
    echo Copiando pasta assets para instalador...
    if exist "instalador\assets" (
        rmdir /s /q "instalador\assets"
    )
    xcopy /E /I /Y "assets" "instalador\assets" >nul
    echo Pasta assets copiada com sucesso!
) else (
    echo Aviso: Pasta assets nao encontrada.
)

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

