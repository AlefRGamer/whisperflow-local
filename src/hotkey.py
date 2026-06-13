"""Atalho global via lib `keyboard`, com supressão do atalho de sistema.

Suprimir o Win+H (substituir o Ditado por Voz do Windows) exige que o processo
rode como administrador. Sem privilégio, o registro com `suppress=True` pode
falhar — nesse caso registramos sem supressão e avisamos no console.
"""
import keyboard


class HotkeyManager:
    def __init__(self):
        self._handle = None
        self._combo: str | None = None

    def register(self, combo: str, callback, suppress: bool = True) -> bool:
        """(Re)registra o atalho. Retorna True se a supressão foi aplicada."""
        self.unregister()
        self._combo = combo
        try:
            self._handle = keyboard.add_hotkey(
                combo, callback, suppress=suppress, trigger_on_release=False
            )
            if suppress:
                print(f"[hotkey] '{combo}' registrado (substituindo o do Windows).")
            return suppress
        except Exception as exc:  # noqa: BLE001 — falta de admin, etc.
            print(
                f"[hotkey] supressão de '{combo}' falhou ({exc}). "
                "Rode como ADMINISTRADOR para substituir o ditado nativo. "
                "Registrando sem supressão..."
            )
            self._handle = keyboard.add_hotkey(
                combo, callback, suppress=False, trigger_on_release=False
            )
            return False

    def unregister(self) -> None:
        if self._handle is not None:
            try:
                keyboard.remove_hotkey(self._handle)
            except (KeyError, ValueError):
                pass
            self._handle = None
