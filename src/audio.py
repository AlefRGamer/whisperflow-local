"""Captura de áudio do microfone."""
from collections.abc import Callable

import numpy as np
import sounddevice as sd


class AudioRecorder:
    """Grava áudio do microfone enquanto o stream estiver ativo.

    Acumula blocos em memória; `stop()` retorna o áudio como float32 mono
    no formato esperado pelo Whisper. Se `on_level` for fornecido, é chamado
    a cada bloco com o nível (RMS, 0..1) para visualização em tempo real.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        on_level: Callable[[float], None] | None = None,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.on_level = on_level
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def _callback(self, indata, frames, time, status):  # noqa: ANN001
        if status:
            print(f"[audio] {status}")
        self._frames.append(indata.copy())
        if self.on_level is not None:
            rms = float(np.sqrt(np.mean(np.square(indata))))
            self.on_level(rms)

    def start(self) -> None:
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if not self._frames:
            return np.zeros(0, dtype=np.float32)
        audio = np.concatenate(self._frames, axis=0)
        return audio.flatten().astype(np.float32)
