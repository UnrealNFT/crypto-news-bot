#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
VENV_PY="$SCRIPT_DIR/.venv/bin/python"

if [ ! -f "$VENV_PY" ]; then
    echo "Error: Virtual environment not found at .venv/"
    exit 1
fi

cd "$SCRIPT_DIR" && "$VENV_PY" -m bot.main
