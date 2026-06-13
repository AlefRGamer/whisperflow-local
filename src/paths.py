"""Resolução de caminhos de dados — permite alocar tudo no disco D.

Para não encher o disco C, settings, histórico e (principalmente) o cache dos
modelos Whisper (~3 GB para o large-v3) ficam numa "pasta de dados" configurável,
por padrão em `D:\\WhisperFlowLocal`.

Um pequeno ponteiro (`location.json`, poucos bytes) fica em `%APPDATA%` apenas para
lembrar onde está a pasta de dados real — esse é o único resíduo no disco C.
"""
import json
import os
import shutil

# Ponteiro mínimo no C: (essencial) que aponta para a pasta de dados real.
_BOOTSTRAP_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")), "WhisperFlowLocal"
)
_BOOTSTRAP_FILE = os.path.join(_BOOTSTRAP_DIR, "location.json")

# Padrão: disco D, se existir; senão, o próprio diretório do ponteiro.
_DEFAULT_DATA_DIR = (
    r"D:\WhisperFlowLocal" if os.path.exists("D:\\") else _BOOTSTRAP_DIR
)


def get_data_dir() -> str:
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
    """Move os dados existentes para `new_dir` e atualiza o ponteiro."""
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
