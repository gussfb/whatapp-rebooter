@echo off
SETLOCAL EnableDelayedExpansion

REM Define arquivo de log
set LOG_FILE=build.log

REM Limpa log anterior
if exist "%LOG_FILE%" del "%LOG_FILE%"

REM Muda para o diretório onde o script está localizado
cd /d "%~dp0"

echo ============================================ >> "%LOG_FILE%"
echo BUILD LOG - %DATE% %TIME% >> "%LOG_FILE%"
echo ============================================ >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

echo Diretorio atual: %CD%
echo Diretorio atual: %CD% >> "%LOG_FILE%"
echo.
echo. >> "%LOG_FILE%"

REM Cria a pasta de output ANTES de tudo
if not exist "dist" (
    echo Creating dist folder...
    echo Creating dist folder... >> "%LOG_FILE%"
    mkdir dist
    echo Dist folder created!
    echo Dist folder created! >> "%LOG_FILE%"
) else (
    echo Dist folder already exists.
    echo Dist folder already exists. >> "%LOG_FILE%"
)
echo.
echo. >> "%LOG_FILE%"

echo Instalando dependencias...
echo Instalando dependencias... >> "%LOG_FILE%"
echo ---------------------------------------- >> "%LOG_FILE%"
pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERRO ao instalar dependencias do requirements.txt!
    echo ERRO ao instalar dependencias do requirements.txt! >> "%LOG_FILE%"
    echo Verifique o arquivo build.log para detalhes.
    pause
    exit /b 1
)

pip install pyinstaller >> "%LOG_FILE%" 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERRO ao instalar pyinstaller!
    echo ERRO ao instalar pyinstaller! >> "%LOG_FILE%"
    echo Verifique o arquivo build.log para detalhes.
    pause
    exit /b 1
)
echo Dependencias instaladas com sucesso!
echo Dependencias instaladas com sucesso! >> "%LOG_FILE%"

echo.
echo Criando executavel...
echo.

REM Verifica se o diretorio src existe
if not exist "src" (
    echo ERRO: Diretorio src nao encontrado!
    echo ERRO: Diretorio src nao encontrado! >> "%LOG_FILE%"
    pause
    exit /b 1
)

REM Limpa arquivo .spec antigo se existir (pode ter configurações incorretas)
if exist "dist\WhatsAppRebooter.spec" (
    echo Cleaning old .spec file...
    echo Cleaning old .spec file... >> "%LOG_FILE%"
    del "dist\WhatsAppRebooter.spec"
)

REM Verifica se o executável está aberto
echo Verificando se WhatsAppRebooter.exe esta em execucao...
echo Verificando se WhatsAppRebooter.exe esta em execucao... >> "%LOG_FILE%"
echo [DEBUG] Passo 1: Verificacao de processo iniciada >> "%LOG_FILE%"

REM Deletar executável antigo se existir e não estiver em uso
if exist "dist\WhatsAppRebooter.exe" (
    echo [DEBUG] Attempting to delete old executable... >> "%LOG_FILE%"
    del "dist\WhatsAppRebooter.exe" 2>NUL
    if exist "dist\WhatsAppRebooter.exe" (
        echo.
        echo ========================================
        echo WARNING: Could not delete old executable.
        echo WhatsAppRebooter.exe may be in use.
        echo Close the application and try again.
        echo ========================================
        echo.
        echo ERROR: Executable in use >> "%LOG_FILE%"
        pause
        exit /b 1
    ) else (
        echo [DEBUG] Old executable deleted successfully. >> "%LOG_FILE%"
    )
) else (
    echo [DEBUG] No old executable found. >> "%LOG_FILE%"
)

echo [DEBUG] Passo 2: Verificacao de processo concluida >> "%LOG_FILE%"

REM Verifica se existe ícone
set USE_ICON=0
if exist "assets\icon.ico" (
    set USE_ICON=1
    echo Icone encontrado: assets\icon.ico
    echo Icone encontrado: assets\icon.ico >> "%LOG_FILE%"
) else (
    echo Aviso: Icone nao encontrado em assets\icon.ico
    echo Aviso: Icone nao encontrado em assets\icon.ico >> "%LOG_FILE%"
    echo Continuando sem icone...
)

REM Executa o PyInstaller
REM Usa caminho relativo para o ícone (mais confiável)
echo. >> "%LOG_FILE%"
echo ---------------------------------------- >> "%LOG_FILE%"
echo PYINSTALLER OUTPUT: >> "%LOG_FILE%"
echo ---------------------------------------- >> "%LOG_FILE%"

if "%USE_ICON%"=="1" (
    echo Running PyInstaller with icon...
    echo Running PyInstaller with icon... >> "%LOG_FILE%"
    pyinstaller --clean --onefile --windowed --name "WhatsAppRebooter" --icon=assets\icon.ico --distpath "dist" --workpath "dist\build" --paths "." --collect-submodules src --hidden-import win32timezone main.py >> "%LOG_FILE%" 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo ========================================
        echo ERROR: PyInstaller failed!
        echo Check build.log for complete details.
        echo ========================================
        echo.
        echo ERROR: PyInstaller failed! >> "%LOG_FILE%"
        type "%LOG_FILE%"
        pause
        exit /b 1
    )
) else (
    echo Running PyInstaller without icon...
    echo Running PyInstaller without icon... >> "%LOG_FILE%"
    pyinstaller --clean --onefile --windowed --name "WhatsAppRebooter" --distpath "dist" --workpath "dist\build" --paths "." --collect-submodules src --hidden-import win32timezone main.py >> "%LOG_FILE%" 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo ========================================
        echo ERROR: PyInstaller failed!
        echo Check build.log for complete details.
        echo ========================================
        echo.
        echo ERROR: PyInstaller failed! >> "%LOG_FILE%"
        type "%LOG_FILE%"
        pause
        exit /b 1
    )
)
echo PyInstaller executed successfully!
echo PyInstaller executed successfully! >> "%LOG_FILE%"

REM Move o arquivo .spec para a pasta dist se foi gerado na raiz
if exist "WhatsAppRebooter.spec" (
    if not exist "dist\WhatsAppRebooter.spec" (
        move "WhatsAppRebooter.spec" "dist\WhatsAppRebooter.spec" >nul
    ) else (
        del "WhatsAppRebooter.spec"
    )
)

REM Copia pasta assets para dist (para ícones e recursos)
if exist "assets" (
    echo Copying assets folder to dist...
    echo Copying assets folder to dist... >> "%LOG_FILE%"
    if exist "dist\assets" (
        rmdir /s /q "dist\assets"
    )
    xcopy /E /I /Y "assets" "dist\assets" >nul 2>&1
    echo Assets folder copied successfully!
    echo Assets folder copied successfully! >> "%LOG_FILE%"
) else (
    echo Warning: Assets folder not found.
    echo Warning: Assets folder not found. >> "%LOG_FILE%"
)

echo.
echo [DEBUG] Finalizing script...
echo [DEBUG] Finalizing script... >> "%LOG_FILE%"
echo.
echo. >> "%LOG_FILE%"
echo ========================================
echo ======================================== >> "%LOG_FILE%"
if exist "dist\WhatsAppRebooter.exe" (
    echo SUCCESS! Executable created at:
    echo SUCCESS! Executable created at: >> "%LOG_FILE%"
    echo %CD%\dist\WhatsAppRebooter.exe
    echo %CD%\dist\WhatsAppRebooter.exe >> "%LOG_FILE%"
    echo.
    echo. >> "%LOG_FILE%"
    echo Size:
    echo Size: >> "%LOG_FILE%"
    dir "dist\WhatsAppRebooter.exe" | find "WhatsAppRebooter.exe"
    dir "dist\WhatsAppRebooter.exe" | find "WhatsAppRebooter.exe" >> "%LOG_FILE%"
) else (
    echo ERROR: Executable was not created!
    echo ERROR: Executable was not created! >> "%LOG_FILE%"
    echo Check error messages above.
    echo Check build.log for details.
)
echo ========================================
echo ======================================== >> "%LOG_FILE%"
echo.
echo. >> "%LOG_FILE%"
echo [INFO] Complete log saved at: %CD%\build.log
echo [INFO] Complete log saved at: %CD%\build.log >> "%LOG_FILE%"
echo.
echo Press any key to open dist folder...
pause >nul
if exist "dist" (
    echo Opening dist folder...
    echo Opening dist folder... >> "%LOG_FILE%"
    explorer dist
)

echo.
echo [DEBUG] Script finalizado com sucesso!
echo [DEBUG] Script finalizado com sucesso! >> "%LOG_FILE%"

