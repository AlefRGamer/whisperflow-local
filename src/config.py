"""Configurações do WhisperFlow Local (persistidas em JSON)."""
import json
import os
from dataclasses import asdict, dataclass

from paths import settings_path


@dataclass
class Config:
    # --- Modelo (faster-whisper) ---
    # tamanhos: tiny, base, small, medium, large-v3
    # RTX 4060 (8 GB) roda large-v3 em float16 em tempo real.
    model_size: str = "large-v3"
    device: str = "cuda"            # "cuda" (RTX 4060) ou "cpu"
    compute_type: str = "float16"   # "float16" (GPU) ou "int8" (CPU)
    language: str | None = "pt"     # None = detecção automática

    # --- Áudio ---
    sample_rate: int = 16000
    channels: int = 1

    # --- Atalho ---
    # Sintaxe da lib `keyboard`. Padrão substitui o Ditado por Voz do Windows.
    hotkey: str = "windows+h"
    # "toggle" (aperta p/ iniciar, aperta p/ parar) — recomendado p/ Win+H.
    mode: str = "toggle"
    # suprime o atalho para o Windows não abrir o ditado nativo (precisa admin).
    suppress_hotkey: bool = True

    # --- Comportamento ---
    type_output: bool = True        # digita no app ativo
    print_output: bool = True

    @classmethod
    def load(cls) -> "Config":
        try:
            with open(settings_path(), encoding="utf-8") as f:
                data = json.load(f)
            known = {k: v for k, v in data.items() if k in cls.__annotations__}
            return cls(**known)
        except (FileNotFoundError, json.JSONDecodeError):
            return cls()

    def save(self) -> None:
        path = settings_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)
