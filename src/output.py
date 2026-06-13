"""Inserção do texto transcrito no aplicativo ativo."""
from pynput.keyboard import Controller


class TextOutput:
    def __init__(self):
        self._keyboard = Controller()

    def type_text(self, text: str) -> None:
        """Digita o texto onde o cursor estiver."""
        if not text:
            return
        self._keyboard.type(text + " ")
