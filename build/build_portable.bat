@echo off
REM ==============================================================
REM  Gera a versao PORTATIL (Windows) com Python EMBUTIDO.
REM  Resultado: pasta WhisperFlow-Portable\ que roda em qualquer
REM  PC Windows SEM Python instalado. Basta copiar e dar 2 cliques.
REM
REM  Pre-requisitos para GERAR (so na sua maquina): curl (vem no
REM  Windows 10+) e conexao com a internet.
REM ==============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0.."

set PY_VER=3.12.8
set OUT=WhisperFlow-Portable
set PYDIR=%OUT%\python

echo === Limpando saida anterior ===
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%PYDIR%"

echo === [1/6] Baixando Python embeddable %PY_VER% ===
curl -L -o "%OUT%\python-embed.zip" ^
  "https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-embed-amd64.zip"
tar -xf "%OUT%\python-embed.zip" -C "%PYDIR%"
del "%OUT%\python-embed.zip"

echo === [2/6] Habilitando 'site' no Python embeddable ===
REM descomenta a linha 'import site' no arquivo ._pth
for %%f in ("%PYDIR%\python*._pth") do (
  powershell -NoProfile -Command ^
    "(Get-Content '%%f') -replace '#import site','import site' | Set-Content '%%f'"
)

echo === [3/6] Instalando o pip ===
curl -L -o "%PYDIR%\get-pip.py" https://bootstrap.pypa.io/get-pip.py
"%PYDIR%\python.exe" "%PYDIR%\get-pip.py" --no-warn-script-location
del "%PYDIR%\get-pip.py"

echo === [4/6] Instalando dependencias (com GPU/CUDA) ===
REM Troque para requirements-cpu.txt para um portatil leve (sem CUDA).
"%PYDIR%\python.exe" -m pip install --no-warn-script-location -r requirements.txt

echo === [5/6] Copiando o programa ===
xcopy /e /i /y src "%OUT%\src" >nul
copy /y requirements.txt "%OUT%\" >nul
copy /y MANUAL.md "%OUT%\" >nul
REM marca como portatil: dados ficam em %OUT%\data
echo portatil > "%OUT%\portable.txt"

echo === [6/6] Criando atalhos de inicio ===
> "%OUT%\Iniciar WhisperFlow.bat" echo @echo off
>> "%OUT%\Iniciar WhisperFlow.bat" echo cd /d "%%~dp0src"
>> "%OUT%\Iniciar WhisperFlow.bat" echo start "" "%%~dp0python\pythonw.exe" main.py

echo.
echo ==============================================================
echo  PRONTO! Pasta gerada: %OUT%\
echo  Copie essa pasta para onde quiser e de 2 cliques em
echo  "Iniciar WhisperFlow.bat". O modelo (~3GB) baixa na 1a vez.
echo ==============================================================
pause
