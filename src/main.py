"""WhisperFlow Local — ditado por voz residente, 100% local (estilo Wispr Flow).

Substitui o Ditado por Voz do Windows: aperte **Win+H** para iniciar a gravação
(overlay com ondas sonoras aparece), aperte **Win+H** de novo para parar — o áudio
é transcrito na GPU e o texto é digitado no campo ativo. Cada transcrição vai para
o histórico, acessível pela janela (ícone na bandeja).

Rode como ADMINISTRADOR para suprimir o atalho nativo do Windows.
"""
import sys
import threading

from PySide6 import QtCore, QtWidgets

from audio import AudioRecorder
from config import Config
from hotkey import HotkeyManager
from output import TextOutput
from overlay import Overlay
from store import History
from theme import apply_dark_theme
from transcriber import Transcriber
from window import MainWindow


class Bridge(QtCore.QObject):
    """Sinais cross-thread -> thread da GUI."""

    level = QtCore.Signal(float)
    rec_started = QtCore.Signal()
    transcribing = QtCore.Signal()
    finished = QtCore.Signal()
    new_entry = QtCore.Signal(dict)


class WhisperFlow:
    def __init__(self, config: Config):
        self.config = config
        self.bridge = Bridge()
        self.history = History()
        self.overlay = Overlay()
        self.recorder = AudioRecorder(
            config.sample_rate, config.channels, on_level=self.bridge.level.emit
        )
        self.transcriber = Transcriber(config)
        self.output = TextOutput() if config.type_output else None
        self.hotkeys = HotkeyManager()
        self._recording = False
        self._busy = False

        self.window = MainWindow(
            config, self.history, on_apply=self._apply_config, on_quit=self.quit
        )

        # sinais -> overlay e janela
        self.bridge.level.connect(self.overlay.push_level)
        self.bridge.rec_started.connect(self.overlay.show_recording)
        self.bridge.transcribing.connect(self.overlay.show_transcribing)
        self.bridge.finished.connect(self.overlay.hide_overlay)
        self.bridge.new_entry.connect(self.window.history_tab.add_entry)

        self._register_hotkey()

    def _register_hotkey(self):
        self.hotkeys.register(
            self.config.hotkey, self._toggle, suppress=self.config.suppress_hotkey
        )

    # --- chamado pela thread do `keyboard` ---
    def _toggle(self):
        if self._busy:
            return
        if not self._recording:
            self._recording = True
            print("[rec] gravando...")
            self.recorder.start()
            self.bridge.rec_started.emit()
        else:
            self._recording = False
            self._busy = True
            self.bridge.transcribing.emit()
            threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        try:
            audio = self.recorder.stop()
            text = self.transcriber.transcribe(audio)
            if self.config.print_output:
                print(f"[texto] {text!r}")
            if self.output and text:
                self.output.type_text(text)
            if text:
                entry = self.history.add(text)
                self.bridge.new_entry.emit(entry)
        except Exception as exc:  # noqa: BLE001 — nunca deixar o app travado
            print(f"[erro] falha na transcrição: {exc}")
        finally:
            # libera SEMPRE o overlay e o estado, mesmo se algo falhar
            self.bridge.finished.emit()
            self._busy = False

    # --- chamado pela GUI ao salvar configurações ---
    def _apply_config(self, config: Config):
        self.config = config
        self.output = TextOutput() if config.type_output else None
        self.recorder.sample_rate = config.sample_rate
        self._register_hotkey()
        threading.Thread(
            target=self.transcriber.reload, args=(config,), daemon=True
        ).start()
        print("[config] configurações aplicadas.")

    def quit(self):
        self.hotkeys.unregister()
        QtWidgets.QApplication.instance().quit()

    def run(self):
        print(
            f"WhisperFlow Local pronto. Aperte '{self.config.hotkey}' para ditar "
            "(toggle). Janela na bandeja do sistema."
        )


def main():
    config = Config.load()
    app = QtWidgets.QApplication(sys.argv)
    apply_dark_theme(app)  # interface escura
    app.setQuitOnLastWindowClosed(False)  # residente na bandeja
    flow = WhisperFlow(config)
    flow.run()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
