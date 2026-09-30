#!/usr/bin/env bash
# Linux/macOS: prepara a base de demonstração e inicia o sistema em http://127.0.0.1:5000
set -euo pipefail
cd "$(dirname "$0")"
.venv/bin/python -m scripts.seed_demo
.venv/bin/python app.py
