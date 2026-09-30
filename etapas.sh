#!/usr/bin/env bash
# Linux/macOS: reproduz todas as etapas (equivalente a etapas.ps1).
# Uso: ./etapas.sh            (tudo, ~10 min)
#      ./etapas.sh --sem-mutacao
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
PY=.venv/bin/python
MUT=.venv-mutation/bin/python
[ -x "$PY" ] || { echo "Execute ./setup.sh primeiro."; exit 1; }

echo "== Métricas de código (radon, pygount) sobre o upstream"
"$PY" scripts/metricas_codigo.py
for etapa in funcional-original estrutural-original suite-corrigida secundarios-original secundarios-corrigida; do
  echo "== Etapa $etapa"
  "$PY" scripts/etapas.py "$etapa"
done
if [ "${1:-}" != "--sem-mutacao" ]; then
  for rodada in inicial final; do
    echo "== Mutação ($rodada)"
    "$MUT" scripts/mutacao.py "$rodada"
  done
fi
echo "== Suíte final"
"$PY" scripts/etapas.py final-corrigida
"$PY" scripts/evolucao.py
echo "Evidências em ./evidencias/"
