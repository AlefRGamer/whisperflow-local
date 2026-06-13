@echo off
REM ==============================================================
REM  Gera o EXECUTAVEL (.exe) com PyInstaller.
REM  Resultado: build\dist\WhisperFlow\WhisperFlow.exe
REM  (uma pasta com o .exe + bibliotecas; o modelo baixa na 1a vez)
REM
REM  Requer um ambiente Python com as dependencias do app ja
REM  instaladas. Reaproveita o .venv da raiz, se existir.
REM ==============================================================
setlocal
cd /d "%~dp0"

set PY=..\.venv\Scripts\python.exe
if not exist "%PY%" set PY=python

echo === Instalando o PyInstaller ===
"%PY%" -m pip install --upgrade pyinstaller

echo === Gerando o executavel ===
"%PY%" -m PyInstaller --noconfirm --clean ^
  --distpath dist --workpath work --specpath . whisperflow.spec

REM ativa modo portatil para o .exe (dados ao lado do executavel)
echo portatil > "dist\WhisperFlow\portable.txt"

echo.
echo ==============================================================
echo  PRONTO! Executavel em: build\dist\WhisperFlow\WhisperFlow.exe
echo  Copie a pasta WhisperFlow\ inteira para usar/compartilhar.
echo ==============================================================
pause
