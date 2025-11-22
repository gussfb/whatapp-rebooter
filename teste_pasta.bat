@echo off
cd /d "%~dp0"
echo Diretorio atual: %CD%
echo.
echo Testando criacao da pasta instalador...
if not exist "instalador" (
    mkdir instalador
    echo Pasta criada com sucesso!
) else (
    echo Pasta ja existe!
)
echo.
dir instalador
echo.
pause

