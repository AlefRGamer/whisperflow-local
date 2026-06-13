"""Resolução de caminhos de dados — suporta modo portátil e modo instalado.

Modo PORTÁTIL (recomendado para levar em pendrive / compartilhar):
    Se existir um arquivo `portable.txt` na raiz do programa (ou a variável de
    ambiente WHISPERFLOW_PORTABLE=1), todos os dados — settings, histórico e o
    cache dos modelos (~3 GB) — ficam numa subpasta `data/` ao lado do programa.
    Assim a pasta inteira é autocontida: copie para qualquer lugar e funciona.

Modo INSTALADO (padrão antigo):
    Para não encher o disco C, os dados ficam numa "pasta de dados" configurável,
    por padrão `D:\\WhisperFlowLocal`. Um ponteiro de poucos bytes em `%APPDATA%`
    (`location.json`) lembra onde ela está — único resíduo no disco C.
"""
import json
import os
import shutil
import sys

# Raiz do programa = pasta que contém `src/` (ou o diretório do .exe empacotado).
if getattr(sys, "frozen", False):  # PyInstaller
    PROGRAM_ROOT = os.path.dirname(sys.executable)
else:
    PROGRAM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ponteiro mínimo no C: (essencial) que aponta para a pasta de dados real.
_BOOTSTRAP_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")), "WhisperFlowLocal"
)
_BOOTSTRAP_FILE = os.path.join(_BOOTSTRAP_DIR, "location.json")

# Padrão (modo instalado): disco D, se existir; senão, o diretório do ponteiro.
_DEFAULT_DATA_DIR = (
    r"D:\WhisperFlowLocal" if os.path.exists("D:\\") else _BOOTSTRAP_DIR
)


def is_portable() -> bool:
    return (
        os.environ.get("WHISPERFLOW_PORTABLE") == "1"
        or os.path.exists(os.path.join(PROGRAM_ROOT, "portable.txt"))
    )


def get_data_dir() -> str:
    # Modo portátil: dados ao lado do programa (pasta autocontida).
    if is_portable():
        return os.path.join(PROGRAM_ROOT, "data")
    # Modo instalado: ponteiro -> pasta configurável.
    try:
        with open(_BOOTSTRAP_FILE, encoding="utf-8") as f:
            data_dir = json.load(f).get("data_dir")
        if data_dir:
            return data_dir
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return _DEFAULT_DATA_DIR


def _write_pointer(data_dir: str) -> None:
    os.makedirs(_BOOTSTRAP_DIR, exist_ok=True)
    with open(_BOOTSTRAP_FILE, "w", encoding="utf-8") as f:
        json.dump({"data_dir": data_dir}, f, ensure_ascii=False, indent=2)


def set_data_dir(new_dir: str) -> None:
    """Move os dados existentes para `new_dir` e atualiza o ponteiro.

    No modo portátil os dados são sempre `data/` ao lado do programa, então
    trocar a pasta é ignorado (mantém a portabilidade).
    """
    if is_portable():
        return
    old_dir = get_data_dir()
    new_dir = os.path.abspath(new_dir)
    os.makedirs(new_dir, exist_ok=True)
    if os.path.abspath(old_dir) != new_dir and os.path.isdir(old_dir):
        for name in ("settings.json", "history.json", "models"):
            src = os.path.join(old_dir, name)
            dst = os.path.join(new_dir, name)
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.move(src, dst)
    _write_pointer(new_dir)


def settings_path() -> str:
    return os.path.join(get_data_dir(), "settings.json")


def history_path() -> str:
    return os.path.join(get_data_dir(), "history.json")


def model_cache_dir() -> str:
    """Onde o faster-whisper baixa/guarda os modelos."""
    path = os.path.join(get_data_dir(), "models")
    os.makedirs(path, exist_ok=True)
    return path
