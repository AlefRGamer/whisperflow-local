# PyInstaller spec — gera um executável do WhisperFlow Local.
# Uso: veja build_exe.bat (instala o pyinstaller e roda este spec).
#
# Observações:
# - PySide6, faster-whisper e ctranslate2 precisam de coleta completa.
# - O modelo (~3 GB) NÃO é embutido: baixa na 1ª execução para a pasta `data/`
#   ao lado do .exe (modo portátil ativado via portable.txt incluído).
# - Com CUDA o executável fica grande (~2 GB). Para um .exe leve, instale o
#   ambiente com requirements-cpu.txt antes de gerar.

from PyInstaller.utils.hooks import collect_all, collect_submodules

datas, binaries, hiddenimports = [], [], []
for pkg in ("faster_whisper", "ctranslate2", "av", "tokenizers"):
    d, b, h = collect_all(pkg)
    datas += d; binaries += b; hiddenimports += h

hiddenimports += collect_submodules("PySide6")

block_cipher = None

a = Analysis(
    ["../src/main.py"],
    pathex=["../src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="WhisperFlow",
    console=False,          # app de bandeja, sem janela de console
    disable_windowed_traceback=False,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    name="WhisperFlow",     # gera dist/WhisperFlow/WhisperFlow.exe
)
