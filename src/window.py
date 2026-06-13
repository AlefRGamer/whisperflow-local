"""Janela principal: histórico de transcrições + configurações + bandeja."""
import os
from collections.abc import Callable

from PySide6 import QtCore, QtGui, QtWidgets

import paths
from config import Config
from store import History

_MODELS = ["tiny", "base", "small", "medium", "large-v3"]
_DEVICES = ["cuda", "cpu"]
_MODES = ["toggle"]


def make_icon() -> QtGui.QIcon:
    """Ícone simples gerado em runtime (círculo azul com microfone estilizado)."""
    pix = QtGui.QPixmap(64, 64)
    pix.fill(QtCore.Qt.transparent)
    p = QtGui.QPainter(pix)
    p.setRenderHint(QtGui.QPainter.Antialiasing)
    p.setBrush(QtGui.QColor(99, 179, 255))
    p.setPen(QtCore.Qt.NoPen)
    p.drawEllipse(6, 6, 52, 52)
    p.setBrush(QtGui.QColor(20, 20, 24))
    p.drawRoundedRect(26, 18, 12, 22, 6, 6)
    p.setPen(QtGui.QPen(QtGui.QColor(20, 20, 24), 3))
    p.drawArc(20, 30, 24, 18, 0, -180 * 16)
    p.drawLine(32, 46, 32, 52)
    p.end()
    return QtGui.QIcon(pix)


class HistoryTab(QtWidgets.QWidget):
    def __init__(self, history: History):
        super().__init__()
        self.history = history
        layout = QtWidgets.QHBoxLayout(self)

        self.list = QtWidgets.QListWidget()
        self.list.setMinimumWidth(220)
        self.list.currentItemChanged.connect(self._on_select)
        layout.addWidget(self.list, 1)

        right = QtWidgets.QVBoxLayout()
        self.editor = QtWidgets.QTextEdit()
        self.editor.setPlaceholderText("Selecione uma transcrição para ver/editar.")
        right.addWidget(self.editor)

        buttons = QtWidgets.QHBoxLayout()
        self.btn_save = QtWidgets.QPushButton("Salvar alteração")
        self.btn_copy = QtWidgets.QPushButton("Copiar")
        self.btn_delete = QtWidgets.QPushButton("Excluir")
        self.btn_save.clicked.connect(self._save)
        self.btn_copy.clicked.connect(self._copy)
        self.btn_delete.clicked.connect(self._delete)
        for b in (self.btn_save, self.btn_copy, self.btn_delete):
            buttons.addWidget(b)
        right.addLayout(buttons)
        layout.addLayout(right, 2)

        self.reload()

    def reload(self):
        self.list.clear()
        for entry in self.history.all():
            preview = entry["text"][:40].replace("\n", " ") or "(vazio)"
            item = QtWidgets.QListWidgetItem(f'{entry["timestamp"]}\n{preview}')
            item.setData(QtCore.Qt.UserRole, entry["id"])
            self.list.addItem(item)

    @QtCore.Slot(dict)
    def add_entry(self, entry: dict):
        self.reload()
        if self.list.count():
            self.list.setCurrentRow(0)  # mais recente primeiro

    def _current_id(self) -> str | None:
        item = self.list.currentItem()
        return item.data(QtCore.Qt.UserRole) if item else None

    def _on_select(self, current, _previous):
        if not current:
            self.editor.clear()
            return
        entry_id = current.data(QtCore.Qt.UserRole)
        for e in self.history.all():
            if e["id"] == entry_id:
                self.editor.setPlainText(e["text"])
                break

    def _save(self):
        entry_id = self._current_id()
        if entry_id:
            self.history.update(entry_id, self.editor.toPlainText())
            self.reload()

    def _copy(self):
        QtWidgets.QApplication.clipboard().setText(self.editor.toPlainText())

    def _delete(self):
        entry_id = self._current_id()
        if entry_id:
            self.history.delete(entry_id)
            self.editor.clear()
            self.reload()


class SettingsTab(QtWidgets.QWidget):
    def __init__(self, config: Config, on_apply: Callable[[Config], None]):
        super().__init__()
        self.config = config
        self.on_apply = on_apply
        form = QtWidgets.QFormLayout(self)

        self.model = QtWidgets.QComboBox()
        self.model.addItems(_MODELS)
        self.model.setCurrentText(config.model_size)

        self.device = QtWidgets.QComboBox()
        self.device.addItems(_DEVICES)
        self.device.setCurrentText(config.device)

        self.language = QtWidgets.QLineEdit(config.language or "")
        self.language.setPlaceholderText("ex.: pt (vazio = automático)")

        self.hotkey = QtWidgets.QLineEdit(config.hotkey)

        self.mode = QtWidgets.QComboBox()
        self.mode.addItems(_MODES)
        self.mode.setCurrentText(config.mode)

        self.type_output = QtWidgets.QCheckBox("Digitar no app ativo")
        self.type_output.setChecked(config.type_output)

        self.suppress = QtWidgets.QCheckBox(
            "Substituir atalho do Windows (requer admin)"
        )
        self.suppress.setChecked(config.suppress_hotkey)

        # Pasta de dados (settings + histórico + modelos) — por padrão no disco D.
        self.data_dir = QtWidgets.QLineEdit(paths.get_data_dir())
        browse = QtWidgets.QPushButton("Procurar…")
        browse.clicked.connect(self._browse_data_dir)
        data_row = QtWidgets.QHBoxLayout()
        data_row.addWidget(self.data_dir)
        data_row.addWidget(browse)
        data_widget = QtWidgets.QWidget()
        data_widget.setLayout(data_row)

        form.addRow("Modelo", self.model)
        form.addRow("Dispositivo", self.device)
        form.addRow("Idioma", self.language)
        form.addRow("Atalho", self.hotkey)
        form.addRow("Modo", self.mode)
        form.addRow("Pasta de dados/modelos", data_widget)
        form.addRow("", self.type_output)
        form.addRow("", self.suppress)

        note = QtWidgets.QLabel(
            "A pasta de dados guarda settings, histórico e o cache dos modelos "
            "(~3 GB) — mantenha-a no disco D para poupar o C. Mudar a pasta move "
            "os arquivos existentes. Mudanças de modelo/dispositivo recarregam o "
            "Whisper. Para suprimir o Win+H, rode o app como administrador."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: gray;")
        form.addRow(note)

        save = QtWidgets.QPushButton("Salvar configurações")
        save.clicked.connect(self._apply)
        form.addRow(save)

    def _browse_data_dir(self):
        chosen = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Escolha a pasta de dados (disco D recomendado)",
            self.data_dir.text(),
        )
        if chosen:
            self.data_dir.setText(chosen)

    def _apply(self):
        # move dados se a pasta mudou (antes de salvar settings no novo destino)
        new_dir = self.data_dir.text().strip()
        if new_dir and os.path.abspath(new_dir) != os.path.abspath(paths.get_data_dir()):
            try:
                paths.set_data_dir(new_dir)
            except OSError as exc:
                QtWidgets.QMessageBox.warning(
                    self, "Pasta de dados", f"Não foi possível mover os dados:\n{exc}"
                )

        self.config.model_size = self.model.currentText()
        self.config.device = self.device.currentText()
        self.config.compute_type = "float16" if self.config.device == "cuda" else "int8"
        self.config.language = self.language.text().strip() or None
        self.config.hotkey = self.hotkey.text().strip() or "windows+h"
        self.config.mode = self.mode.currentText()
        self.config.type_output = self.type_output.isChecked()
        self.config.suppress_hotkey = self.suppress.isChecked()
        self.config.save()
        self.on_apply(self.config)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, config: Config, history: History,
                 on_apply: Callable[[Config], None], on_quit: Callable[[], None]):
        super().__init__()
        self.setWindowTitle("WhisperFlow Local")
        self.resize(720, 460)
        self.setWindowIcon(make_icon())
        self._on_quit = on_quit

        tabs = QtWidgets.QTabWidget()
        self.history_tab = HistoryTab(history)
        self.settings_tab = SettingsTab(config, on_apply)
        tabs.addTab(self.history_tab, "Histórico")
        tabs.addTab(self.settings_tab, "Configurações")
        self.setCentralWidget(tabs)

        self._build_tray()

    def _build_tray(self):
        self.tray = QtWidgets.QSystemTrayIcon(make_icon(), self)
        self.tray.setToolTip("WhisperFlow Local")
        menu = QtWidgets.QMenu()
        menu.addAction("Abrir", self.show_window)
        menu.addSeparator()
        menu.addAction("Sair", self._on_quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:  # clique simples
            self.show_window()

    def show_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event: QtGui.QCloseEvent):
        # fechar apenas esconde; app continua residente na bandeja
        event.ignore()
        self.hide()
