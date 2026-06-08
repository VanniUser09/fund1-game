@echo off
setlocal
cd /d "%~dp0"

set "PY_CMD="

python --version >nul 2>nul
if not errorlevel 1 (
    set "PY_CMD=python"
)

if "%PY_CMD%"=="" (
    py -3 --version >nul 2>nul
    if not errorlevel 1 (
        set "PY_CMD=py -3"
    )
)

if "%PY_CMD%"=="" (
    echo Python nao foi encontrado de verdade no computador.
    echo.
    echo Instale o Python uma vez com este comando no PowerShell:
    echo winget install Python.Python.3.12
    echo.
    echo Depois feche e abra o terminal novamente, ou de dois cliques neste arquivo.
    pause
    exit /b 1
)

%PY_CMD% -m pip show pygame >nul 2>nul
if errorlevel 1 (
    echo Instalando pygame...
    %PY_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Nao foi possivel instalar o pygame automaticamente.
        echo Tente rodar:
        echo %PY_CMD% -m pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

%PY_CMD% main.py

endlocal
