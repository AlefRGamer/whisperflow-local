"""Transcrição local usando faster-whisper."""
import cuda_setup

cuda_setup.ensure_cuda_dlls()  # registra cuBLAS/cuDNN antes de carregar ctranslate2

import numpy as np  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402

import paths  # noqa: E402
from config import Config  # noqa: E402


class Transcriber:
    def __init__(self, config: Config):
        self.config = config
        self.model: WhisperModel | None = None
        self.loading = False
        self._load()

    def _load(self) -> None:
        self.loading = True
        print(
            f"[whisper] carregando modelo '{self.config.model_size}' "
            f"({self.config.device}/{self.config.compute_type})..."
        )
        self.model = WhisperModel(
            self.config.model_size,
            device=self.config.device,
            compute_type=self.config.compute_type,
            download_root=paths.model_cache_dir(),  # modelos no disco de dados (D:)
        )
        self.loading = False
        print("[whisper] modelo pronto.")

    def reload(self, config: Config) -> None:
        """Recarrega o modelo se os parâmetros relevantes mudaram."""
        changed = (
            config.model_size != self.config.model_size
            or config.device != self.config.device
            or config.compute_type != self.config.compute_type
        )
        self.config = config
        if changed:
            self._load()

    def transcribe(self, audio: np.ndarray) -> str:
        if audio.size == 0 or self.model is None:
            return ""
        segments, _info = self.model.transcribe(
            audio,
            language=self.config.language,
            beam_size=5,
            vad_filter=True,  # ignora silêncio
        )
        text = " ".join(seg.text.strip() for seg in segments)
        return text.strip()
