#!/usr/bin/env bash
# ============================================================
#  WhisperFlow Local - setup (Linux / macOS)
#  Cria .venv nesta pasta e instala dependencias. Rode UMA vez.
# ============================================================
set -e
cd "$(dirname "$0")"

echo "[1/3] Criando ambiente virtual (.venv)..."
python3 -m venv .venv

echo "[2/3] Atualizando o pip..."
./.venv/bin/python -m pip install --upgrade pip

echo "[3/3] Instalando dependencias..."
# No Linux sem GPU NVIDIA, use requirements-cpu.txt (mais leve).
./.venv/bin/python -m pip install -r requirements.txt

echo
echo "Pronto! Use ./run.sh para iniciar."
echo "Obs (Linux): atalhos globais com a lib 'keyboard' exigem rodar como root"
echo "             (sudo ./run.sh). A digitacao/overlay funcionam sob X11."
