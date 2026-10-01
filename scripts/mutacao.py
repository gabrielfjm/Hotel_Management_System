"""Teste de mutação com Cosmic Ray sobre as funções do recorte em hotel/views.py.

Executar com o Python do ambiente de mutação (.venv-mutation), na raiz do repositório:

    .venv-mutation/Scripts/python.exe scripts/mutacao.py inicial
    .venv-mutation/Scripts/python.exe scripts/mutacao.py final

Escopo: TODOS os mutantes que os operadores padrão do Cosmic Ray geram nas
linhas das funções dos três requisitos principais (reserve, cal_cost e as
auxiliares _sessao_autenticada, _periodos_conflitam, _quartos_ocupados e
_ler_quartos). Não há amostragem. Funções fora do recorte (consulta,
signup, signin, update_reservation, delete_reservation, payment...) não
têm testes por decisão de escopo e são excluídas para não distorcer o escore.

Saídas em evidencias/mutacao-<rodada>/:
    sessao.sqlite     sessão do Cosmic Ray (inspecionável com cosmic-ray dump / cr-report)
    resumo.json       totais, escore e contagem por função e por operador
    sobreviventes.txt diff de cada mutante sobrevivente
    execucao.txt      comandos e saída do cosmic-ray exec
"""

import ast
from collections import Counter, defaultdict
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from cosmic_ray.commands.init import _all_work_items
from cosmic_ray.work_db import WorkDB, use_db
from cosmic_ray.work_item import TestOutcome

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("hotel/views.py")
RECORTE = ("reserve", "cal_cost")
COSMIC_RAY = Path(sys.executable).with_name("cosmic-ray.exe" if sys.platform == "win32" else "cosmic-ray")


def funcoes_do_recorte():
    tree = ast.parse((ROOT / SOURCE).read_text(encoding="utf-8"))
    return {node.name: (node.lineno, node.end_lineno) for node in tree.body
            if isinstance(node, ast.FunctionDef) and (node.name in RECORTE or node.name.startswith("_"))}


def funcao_da_linha(funcoes, linha):
    return next((nome for nome, (ini, fim) in funcoes.items() if ini <= linha <= fim), None)


def itens_do_recorte(funcoes=None):
    """Todos os mutantes dos operadores padrão cujas linhas pertencem às funções do recorte."""
    funcoes = funcoes or funcoes_do_recorte()
    return [item for item in _all_work_items([SOURCE], {})
            if funcao_da_linha(funcoes, item.mutations[0].start_pos[0])]


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("inicial", "final"):
        raise SystemExit("Uso: scripts/mutacao.py inicial|final")
    rodada = sys.argv[1]
    modelo = ROOT / "mutacao" / f"cosmic-ray-{rodada}.toml"
    saida = ROOT / "evidencias" / f"mutacao-{rodada}"
    shutil.rmtree(saida, ignore_errors=True)
    saida.mkdir(parents=True)
    # O Windows não localiza executáveis por caminho relativo no CreateProcess usado pelo
    # Cosmic Ray; a configuração efetiva recebe o caminho absoluto (entre aspas) do pytest.
    python = (ROOT / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")).as_posix()
    config = saida / "cosmic-ray.toml"
    config.write_text(modelo.read_text(encoding="utf-8").replace("{python}", f"\\\"{python}\\\""), encoding="utf-8")
    sessao = saida / "sessao.sqlite"

    funcoes = funcoes_do_recorte()
    itens = itens_do_recorte(funcoes)
    with use_db(str(sessao), WorkDB.Mode.create) as db:
        db.clear()
        db.add_work_items(itens)
    print(f"{len(itens)} mutantes nas funções do recorte")

    comando = [str(COSMIC_RAY), "exec", str(config.relative_to(ROOT)), str(sessao.relative_to(ROOT))]
    inicio = time.monotonic()
    processo = subprocess.run(comando, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    duracao = round(time.monotonic() - inicio, 1)
    (saida / "execucao.txt").write_text(
        f"# Rodada: {rodada}\n# Configuração ({config.relative_to(ROOT)}):\n{config.read_text(encoding='utf-8')}\n"
        f"# Comando: {' '.join(comando[1:])}\n# Duração: {duracao} s; código de saída: {processo.returncode}\n\n"
        f"{processo.stdout}\n{processo.stderr}", encoding="utf-8")
    if processo.returncode != 0:
        raise SystemExit(processo.stderr[-3000:])

    totais = Counter()
    por_funcao = defaultdict(Counter)
    por_operador = defaultdict(Counter)
    sobreviventes = []
    with use_db(str(sessao), WorkDB.Mode.open) as db:
        for item, resultado in db.completed_work_items:
            mutacao = item.mutations[0]
            linha = mutacao.start_pos[0]
            estado = resultado.test_outcome.value if resultado.test_outcome else resultado.worker_outcome.value
            funcao = funcao_da_linha(funcoes, linha)
            totais[estado] += 1
            por_funcao[funcao][estado] += 1
            por_operador[mutacao.operator_name][estado] += 1
            if resultado.test_outcome == TestOutcome.SURVIVED:
                sobreviventes.append({"job_id": item.job_id, "funcao": funcao, "linha": linha,
                                      "operador": mutacao.operator_name, "ocorrencia": mutacao.occurrence,
                                      "diff": resultado.diff})
        pendentes = sum(1 for _ in db.pending_work_items)

    mortos, vivos = totais["killed"], totais["survived"]
    resumo = {
        "rodada": rodada,
        "configuracao": str(config.relative_to(ROOT)),
        "comando": " ".join(comando[1:]),
        "duracao_s": duracao,
        "funcoes": {nome: list(linhas) for nome, linhas in funcoes.items()},
        "total": len(itens),
        "mortos": mortos,
        "sobreviventes": vivos,
        "incompetentes": totais["incompetent"],
        "outros": {k: v for k, v in totais.items() if k not in ("killed", "survived", "incompetent")},
        "pendentes": pendentes,
        "escore_pct": round(100 * mortos / (mortos + vivos), 1) if mortos + vivos else None,
        "por_funcao": {k: dict(v) for k, v in sorted(por_funcao.items())},
        "por_operador": {k: dict(v) for k, v in sorted(por_operador.items())},
        "sobreviventes_lista": [{k: v for k, v in s.items() if k != "diff"} for s in sobreviventes],
    }
    (saida / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    texto = [f"Rodada {rodada}: {len(sobreviventes)} mutantes sobreviventes\n"]
    for s in sorted(sobreviventes, key=lambda s: (s["linha"], s["operador"], s["ocorrencia"])):
        texto.append(f"=== {s['funcao']} linha {s['linha']} | {s['operador']} (ocorrência {s['ocorrencia']}) | job {s['job_id']}")
        texto.append(s["diff"] or "")
    (saida / "sobreviventes.txt").write_text("\n".join(texto), encoding="utf-8")
    print(json.dumps({k: resumo[k] for k in ("total", "mortos", "sobreviventes", "incompetentes", "outros",
                                             "pendentes", "escore_pct", "duracao_s")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
