@echo off
REM ============================================================
REM  WhisperFlow Local - setup (Windows)
REM  Cria um ambiente virtual .venv DENTRO desta pasta e instala
REM  as dependencias. Rode UMA vez apos baixar do GitHub.
REM ============================================================
setlocal
cd /d "%~dp0"

echo [1/3] Criando ambiente virtual (.venv)...
py -3 -m venv .venv 2>nul || python -m venv .venv
if not exist ".venv\Scripts\python.exe" (
  echo ERRO: Python nao encontrado. Instale o Python 3.10+ e tente de novo.
  pause & exit /b 1
)

echo [2/3] Atualizando o pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo [3/3] Instalando dependencias...
REM Use requirements-cpu.txt se NAO tiver GPU NVIDIA (mais leve).
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Pronto! Use run.bat para iniciar (ou de 2 cliques nele).
pause
