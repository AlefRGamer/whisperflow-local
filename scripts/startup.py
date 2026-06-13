"""Instala/remove o WhisperFlow Local na inicialização do Windows.

Uso:
    python scripts/startup.py install        # entrada HKCU Run (sem console, SEM admin)
    python scripts/startup.py uninstall      # remove a entrada HKCU Run
    python scripts/startup.py status

    # Tarefa agendada ELEVADA (sobe como administrador no logon) — necessária
    # para suprimir o Win+H desde o boot. Os dois comandos abaixo precisam ser
    # executados num terminal ABERTO COMO ADMINISTRADOR:
    python scripts/startup.py install-admin  # cria a tarefa elevada (ONLOGON, RL HIGHEST)
    python scripts/startup.py uninstall-admin

A entrada HKCU Run sobe sem console, mas SEM privilégio elevado. Para que o app
substitua o Ditado por Voz nativo (Win+H) automaticamente no boot, use a tarefa
agendada elevada (`install-admin`).
"""
import os
import subprocess
import sys
import winreg

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_NAME = "WhisperFlowLocal"

_PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN = os.path.join(_PROJECT, "src", "main.py")


def _pythonw() -> str:
    """pythonw.exe (sem console) do mesmo ambiente do Python atual."""
    candidate = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return candidate if os.path.exists(candidate) else sys.executable


def _command() -> str:
    return f'"{_pythonw()}" "{_MAIN}"'


def install():
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, _NAME, 0, winreg.REG_SZ, _command())
    print(f"[ok] instalado na inicializacao:\n      {_command()}")


def uninstall():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, _NAME)
        print("[ok] removido da inicializacao.")
    except FileNotFoundError:
        print("[--] nao estava instalado.")


def status():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, _NAME)
        print(f"[HKCU Run] ativo: {value}")
    except FileNotFoundError:
        print("[HKCU Run] inativo.")
    # status da tarefa agendada
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", _NAME],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"[Tarefa agendada] ativa (elevada): {_NAME}")
    else:
        print("[Tarefa agendada] inativa.")


# --- Tarefa agendada elevada (sobe como admin no logon) ---

def install_admin():
    """Cria tarefa ONLOGON com privilégio mais alto. Requer terminal ADMIN."""
    cmd = [
        "schtasks", "/Create",
        "/TN", _NAME,
        "/TR", _command(),       # mesmo pythonw + main.py
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",        # executar com privilégios mais altos (elevado)
        "/F",                    # sobrescreve se já existir
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[ok] tarefa elevada criada:\n      {_command()}")
        print("      Sobe como administrador a cada logon (suprime o Win+H nativo).")
    else:
        print("[erro] falha ao criar a tarefa. Abra o terminal COMO ADMINISTRADOR.")
        print((result.stderr or result.stdout).strip())


def uninstall_admin():
    result = subprocess.run(
        ["schtasks", "/Delete", "/TN", _NAME, "/F"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print("[ok] tarefa agendada removida.")
    else:
        print((result.stderr or result.stdout).strip() or "[--] nada a remover.")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    {
        "install": install,
        "uninstall": uninstall,
        "status": status,
        "install-admin": install_admin,
        "uninstall-admin": uninstall_admin,
    }.get(action, status)()
