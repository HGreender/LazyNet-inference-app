#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/venv/bin/activate"

QT_QPA_PLATFORMTHEME=generic python "$SCRIPT_DIR/lazy_net_inference_app/main.py"