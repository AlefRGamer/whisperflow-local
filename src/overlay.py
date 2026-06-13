"""Overlay flutuante estilo Wispr Flow — pílula com ondas sonoras.

Janela sem borda, translúcida e sempre no topo, posicionada na parte
inferior central da tela. Mostra barras animadas reagindo ao áudio
enquanto grava e um indicador de "transcrevendo" ao finalizar.
"""
import collections

from PySide6 import QtCore, QtGui, QtWidgets

_NUM_BARS = 28
_PILL_W = 240
_PILL_H = 64
_MARGIN_BOTTOM = 80


class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool
            | QtCore.Qt.WindowTransparentForInput  # não rouba foco/cliques
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.resize(_PILL_W, _PILL_H)

        self.state = "idle"  # "recording" | "transcribing"
        self._levels = collections.deque([0.0] * _NUM_BARS, maxlen=_NUM_BARS)
        self._phase = 0.0

        # animação suave (~60 fps)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)

    # --- posicionamento ---
    def _reposition(self):
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        x = screen.center().x() - self.width() // 2
        y = screen.bottom() - self.height() - _MARGIN_BOTTOM
        self.move(x, y)

    # --- API pública (chamar pela thread da GUI via sinais) ---
    @QtCore.Slot()
    def show_recording(self):
        self.state = "recording"
        self._levels = collections.deque([0.0] * _NUM_BARS, maxlen=_NUM_BARS)
        self._reposition()
        self.show()
        self._timer.start(16)

    @QtCore.Slot(float)
    def push_level(self, level: float):
        # normaliza e comprime para algo visível
        v = min(1.0, level * 8.0)
        self._levels.append(v)

    @QtCore.Slot()
    def show_transcribing(self):
        self.state = "transcribing"
        self.update()

    @QtCore.Slot()
    def hide_overlay(self):
        self.state = "idle"
        self._timer.stop()
        self.hide()

    def _tick(self):
        self._phase += 0.25
        self.update()

    # --- desenho ---
    def paintEvent(self, _event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        # pílula de fundo
        rect = self.rect().adjusted(1, 1, -1, -1)
        p.setBrush(QtGui.QColor(20, 20, 24, 220))
        p.setPen(QtCore.Qt.NoPen)
        p.drawRoundedRect(rect, _PILL_H / 2, _PILL_H / 2)

        if self.state == "transcribing":
            self._draw_transcribing(p)
        else:
            self._draw_bars(p)
        p.end()

    def _draw_bars(self, p: QtGui.QPainter):
        cx_pad = 24
        usable_w = self.width() - cx_pad * 2
        bar_w = usable_w / _NUM_BARS * 0.55
        gap = usable_w / _NUM_BARS
        cy = self.height() / 2
        max_h = self.height() * 0.6
        color = QtGui.QColor(99, 179, 255)
        p.setBrush(color)
        for i, lvl in enumerate(self._levels):
            # leve oscilação para parecer "vivo" mesmo em silêncio
            idle = 0.08 * (0.5 + 0.5 * abs((i / _NUM_BARS) - 0.5))
            h = max(2.0, (max(lvl, idle)) * max_h)
            x = cx_pad + i * gap
            p.drawRoundedRect(
                QtCore.QRectF(x, cy - h / 2, bar_w, h), bar_w / 2, bar_w / 2
            )

    def _draw_transcribing(self, p: QtGui.QPainter):
        p.setPen(QtGui.QColor(230, 230, 235))
        font = p.font()
        font.setPointSize(11)
        p.setFont(font)
        dots = "." * (1 + int(self._phase) % 3)
        p.drawText(self.rect(), QtCore.Qt.AlignCenter, f"transcrevendo{dots}")
