"""Coloca as DLLs CUDA (cuBLAS/cuDNN) instaladas via pip no caminho de busca.

As libs `nvidia-cublas-cu12` e `nvidia-cudnn-cu12` ficam em
`site-packages/nvidia/<lib>/bin`, mas o Windows não as procura lá por padrão.
Sem isso, o ctranslate2 falha com "cublas64_12.dll is not found".

IMPORTANTE: importe ESTE módulo antes de `faster_whisper`/`ctranslate2`.
"""
import os
import site
import sys

_added = False


def ensure_cuda_dlls() -> None:
    global _added
    if _added or os.name != "nt":
        return

    roots: list[str] = []
    # diretórios de site-packages do venv atual
    try:
        roots.extend(site.getsitepackages())
    except AttributeError:
        pass
    roots.append(os.path.join(sys.prefix, "Lib", "site-packages"))

    for sp in roots:
        nvidia = os.path.join(sp, "nvidia")
        if not os.path.isdir(nvidia):
            continue
        for lib in os.listdir(nvidia):
            bin_dir = os.path.join(nvidia, lib, "bin")
            if os.path.isdir(bin_dir):
                os.add_dll_directory(bin_dir)
                # também no PATH, por garantia (subprocessos/loaders antigos)
                os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")

    _added = True
