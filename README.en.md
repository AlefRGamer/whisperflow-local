# WhisperFlow Local

**[Português](README.md)** · English

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![Platform: Windows | Linux | macOS](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![Status: Functional](https://img.shields.io/badge/status-functional-brightgreen.svg)

Voice dictation (speech-to-text) running **100% locally** on your own machine — an
offline alternative to apps like Wispr Flow. It captures the microphone, transcribes
with a local Whisper model and types the text wherever your cursor is.

> Full manual: [`MANUAL.md`](MANUAL.md) (Portuguese)

## Quick start (from GitHub)

```bash
git clone https://github.com/AlefRGamer/whisperflow-local.git
cd whisperflow-local
setup.bat      # Windows  (or: bash setup.sh on Linux/macOS) — creates .venv and installs
run.bat        # start    (or: ./run.sh)
```

The model (~3 GB) downloads automatically on first run. For **portable (embedded
Python)** and **.exe** builds, see section 10 of the [MANUAL](MANUAL.md).

## Goal

- Local transcription, without sending audio to the cloud (privacy + no API cost).
- Global shortcut to start/stop dictation in any application.
- Automatic insertion of the transcribed text via keyboard.

## Stack

- **Python 3.10+** (tested on 3.14)
- **Transcription:** [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) (CTranslate2, fast on CPU/GPU)
- **Audio:** `sounddevice` (capture + real-time RMS level)
- **Global shortcut + typing:** `keyboard` / `pynput`
- **UI:** `PySide6` (Qt), dark theme
- **GPU:** RTX 4060 (8 GB) → CUDA + `float16`, runs `large-v3` in real time

## Target hardware

i5-12400 · 32 GB RAM · RTX 4060 (8 GB). Defaults ship for GPU:
`device="cuda"`, `compute_type="float16"`, `model_size="large-v3"`. Without an NVIDIA
GPU the app **falls back to CPU automatically**.

### GPU prerequisite (faster-whisper)

On the `cuda` device, `faster-whisper` needs the **cuBLAS** and **cuDNN 9** libraries.
On Windows they come as pip packages (no full CUDA Toolkit required) and are installed
by `requirements.txt`. The app locates the DLLs automatically (`src/cuda_setup.py`).

## How to use

Resident app (runs in the background, tray icon):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

- Press **`AltGr + Z`** (default shortcut, **toggle** mode) to **start** recording
  → a **sound-wave overlay** appears, reacting to your voice.
- Press **`AltGr + Z`** again to **stop** → the overlay shows "transcrevendo…", the
  text is generated on the GPU and **typed into the active field** (wherever the cursor is).
- Each transcription goes to the **History** (dark-themed window, reachable from the tray).
- To **quit**: tray menu → **Sair** (Quit).

`AltGr+Z` doesn't conflict with Windows and **needs no administrator**. To change the
shortcut, use **Settings → Atalho (Shortcut)**.

### (Optional) Replace Windows' Win+H (administrator)

If you prefer **`Win+H`** (Windows' native Voice Typing shortcut), it must be
**suppressed**, which requires **running as administrator**:

1. In **Settings**, change the shortcut to `windows+h` and tick "Substituir atalho do Windows".
2. **Run the app as administrator.** Without admin, native dictation may pop up too.

### Window (history + settings)

Open it from the tray (click the icon). Two tabs:

- **History:** list of transcriptions; select to **edit**, **Copy** or **Delete**.
- **Settings:** model, device (cuda/cpu), language, shortcut, mode, type into active app,
  replace Windows shortcut, and **data/models folder**. **Save** applies immediately
  (reloads the model if needed).

### Where data lives

By default settings, history and the **model cache** (~3 GB) live in a configurable
**data folder**. In **portable mode** (a `portable.txt` file next to the program) it's
`data/` beside the app; otherwise `D:\WhisperFlowLocal` with a tiny pointer in
`%APPDATA%\WhisperFlowLocal\location.json`.

### Start with Windows

```bash
python scripts/startup.py install     # HKCU Run: starts without console (NO admin)
python scripts/startup.py uninstall
python scripts/startup.py status

# Elevated (needed only for Win+H) — run in an ADMIN terminal:
python scripts/startup.py install-admin
python scripts/startup.py uninstall-admin
```

Use **either** HKCU Run **or** the elevated task, not both.

## Architecture (`src/`)

| File | Role |
|---|---|
| `config.py` | Settings persisted as JSON (model, GPU, key, language) |
| `paths.py` | Resolves the data folder (portable mode or disk D) |
| `cuda_setup.py` | Registers the CUDA DLLs before loading ctranslate2 |
| `store.py` | Transcription history (JSON) |
| `audio.py` | Microphone capture + real-time level (RMS) |
| `transcriber.py` | Transcription with `faster-whisper` (reloadable, GPU→CPU fallback) |
| `output.py` | Types the text into the active app (`pynput`) |
| `hotkey.py` | Global shortcut via `keyboard` (+ optional Win+H suppression) |
| `overlay.py` | Floating sound-wave overlay (PySide6/Qt) |
| `theme.py` | Dark UI theme |
| `window.py` | Window (history + settings) + tray icon |
| `main.py` | Orchestration: toggle hotkey + Qt event loop + threads |

Flow: `AltGr+Z` → `AudioRecorder.start` + overlay; audio levels travel via Qt signals
to the overlay; `AltGr+Z` again → a thread transcribes, types and saves to history,
while the GUI stays responsive.

## License

[MIT](LICENSE) © 2026 Alef Ronaldo
