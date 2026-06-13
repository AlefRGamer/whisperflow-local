"""Tema escuro para a interface (evita o branco que cansa a vista)."""
from PySide6 import QtGui, QtWidgets

# paleta base
_BG = QtGui.QColor(30, 31, 34)        # fundo das janelas
_BASE = QtGui.QColor(24, 25, 28)      # fundo de listas/campos
_PANEL = QtGui.QColor(43, 45, 49)     # botões/abas
_TEXT = QtGui.QColor(225, 227, 230)   # texto
_ACCENT = QtGui.QColor(99, 179, 255)  # azul de destaque (igual ao overlay)
_DISABLED = QtGui.QColor(120, 122, 126)


def apply_dark_theme(app: QtWidgets.QApplication) -> None:
    app.setStyle("Fusion")

    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window, _BG)
    pal.setColor(QtGui.QPalette.WindowText, _TEXT)
    pal.setColor(QtGui.QPalette.Base, _BASE)
    pal.setColor(QtGui.QPalette.AlternateBase, _BG)
    pal.setColor(QtGui.QPalette.ToolTipBase, _BG)
    pal.setColor(QtGui.QPalette.ToolTipText, _TEXT)
    pal.setColor(QtGui.QPalette.Text, _TEXT)
    pal.setColor(QtGui.QPalette.Button, _PANEL)
    pal.setColor(QtGui.QPalette.ButtonText, _TEXT)
    pal.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 80, 80))
    pal.setColor(QtGui.QPalette.Link, _ACCENT)
    pal.setColor(QtGui.QPalette.Highlight, _ACCENT)
    pal.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(15, 16, 18))

    for role in (
        QtGui.QPalette.WindowText, QtGui.QPalette.Text, QtGui.QPalette.ButtonText
    ):
        pal.setColor(QtGui.QPalette.Disabled, role, _DISABLED)

    app.setPalette(pal)

    # ajustes finos (bordas, hover dos botões e abas)
    app.setStyleSheet(
        """
        QWidget { font-size: 10pt; }
        QPushButton {
            background-color: #2b2d31; border: 1px solid #3a3d42;
            border-radius: 6px; padding: 6px 12px;
        }
        QPushButton:hover { background-color: #35383d; }
        QPushButton:pressed { background-color: #404449; }
        QLineEdit, QComboBox, QTextEdit, QListWidget {
            background-color: #18191c; border: 1px solid #3a3d42;
            border-radius: 6px; padding: 4px;
        }
        QListWidget::item:selected { background-color: #2f5f8f; }
        QTabBar::tab {
            background: #2b2d31; padding: 8px 16px; border-radius: 6px; margin: 2px;
        }
        QTabBar::tab:selected { background: #3a6ea5; color: #ffffff; }
        QCheckBox::indicator { width: 16px; height: 16px; }
        """
    )
