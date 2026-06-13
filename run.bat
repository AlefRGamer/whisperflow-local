@echo off
REM Inicia o WhisperFlow Local usando o .venv desta pasta (sem console).
setlocal
cd /d "%~dp0src"
start "" "%~dp0.venv\Scripts\pythonw.exe" main.py
