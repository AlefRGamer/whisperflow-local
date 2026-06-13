#!/usr/bin/env bash
# Inicia o WhisperFlow Local usando o .venv desta pasta.
cd "$(dirname "$0")/src"
exec "../.venv/bin/python" main.py
