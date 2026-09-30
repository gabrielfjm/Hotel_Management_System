#!/usr/bin/env bash
# Linux/macOS: cria .venv (Python 3.9: app, pytest, pytest-cov) e .venv-mutation (Python 3.12: Cosmic Ray).
# Requer uv (https://docs.astral.sh/uv/). Equivalente a setup_local.ps1.
set -euo pipefail
cd "$(dirname "$0")"
uv venv --python 3.9 .venv
uv pip install --python .venv/bin/python -r requirements-test.txt
uv venv --python 3.12 .venv-mutation
uv pip install --python .venv-mutation/bin/python -r requirements-mutation.txt
echo "Ambientes prontos. Use ./etapas.sh ou ./executar.sh."
