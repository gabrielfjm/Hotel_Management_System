"""Seletor de mutantes usado pela ponte do V&V TestLab (opção --cosmic-ray-selector).

Cria a sessão do Cosmic Ray com o mesmo escopo de scripts/mutacao.py: todos os
mutantes das funções do recorte, sem amostragem. Executar com .venv-mutation:

    python scripts/selecionar_mutantes.py <sessao.sqlite> <manifesto.json>
"""

import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.chdir(Path(__file__).resolve().parents[1])

from cosmic_ray.work_db import WorkDB, use_db  # noqa: E402
from mutacao import funcoes_do_recorte, funcao_da_linha, itens_do_recorte  # noqa: E402

sessao, manifesto = Path(sys.argv[1]), Path(sys.argv[2])
funcoes = funcoes_do_recorte()
itens = itens_do_recorte(funcoes)
with use_db(str(sessao), WorkDB.Mode.create) as db:
    db.clear()
    db.add_work_items(itens)
manifesto.write_text(json.dumps([
    {"funcao": funcao_da_linha(funcoes, i.mutations[0].start_pos[0]), "linha": i.mutations[0].start_pos[0],
     "operador": i.mutations[0].operator_name, "ocorrencia": i.mutations[0].occurrence, "job_id": i.job_id}
    for i in itens], ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(itens)} mutantes nas funções do recorte -> {sessao}")
