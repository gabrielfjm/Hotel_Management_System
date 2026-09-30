"""Executa uma etapa de teste e grava as evidências em evidencias/<etapa>/.

Uso (a partir da raiz do repositório, com o Python de .venv):

    python scripts/etapas.py funcional-original
    python scripts/etapas.py estrutural-original
    python scripts/etapas.py suite-corrigida
    python scripts/etapas.py final-corrigida

Cada etapa grava:
    pytest.txt            saída completa do pytest (-v -rxX) e relatório term-missing
    junit.xml             resultado caso a caso
    coverage.json         relatório JSON do coverage.py (comandos e desvios)
    htmlcov/              relatório HTML do coverage.py
    rastreabilidade.json  caso -> etapa -> classes -> defeito
    cobertura-recorte.json  cobertura somente das funções do recorte
"""

import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import io

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

# Funções que implementam as três funcionalidades do recorte. As auxiliares
# (prefixo "_") só existem na versão corrigida e são incluídas quando presentes.
RECORTE = ("reserve", "cal_cost", "check_available", "show_rooms")

ETAPAS = {
    "funcional-original": ("original", "funcional"),
    "estrutural-original": ("original", "funcional or estrutural"),
    "suite-corrigida": ("corrigida", "funcional or estrutural"),
    "final-corrigida": ("corrigida", "funcional or estrutural or mutacao"),
    "secundarios-original": ("original", "secundario"),
    "secundarios-corrigida": ("corrigida", "secundario"),
}


def extrair_original():
    """Extrai hotel/ da tag sut-original para .sut-original/ (código sem correções)."""
    destino = ROOT / ".sut-original"
    shutil.rmtree(destino, ignore_errors=True)
    destino.mkdir()
    arquivo = subprocess.run(["git", "archive", "--format=tar", "sut-original", "hotel"],
                             cwd=ROOT, check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(arquivo)) as tar:
        tar.extractall(destino)


def funcoes_do_recorte(views_path):
    tree = ast.parse(views_path.read_text(encoding="utf-8"))
    nomes = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
    return [n for n in nomes if n in RECORTE or n.startswith("_")]


def cobertura_do_recorte(coverage_json, views_path):
    data = json.loads(coverage_json.read_text(encoding="utf-8"))
    arquivo = next(v for k, v in data["files"].items() if k.replace("\\", "/").endswith("hotel/views.py"))
    por_funcao = {}
    total = {"comandos": 0, "comandos_cobertos": 0, "desvios": 0, "desvios_cobertos": 0}
    for nome in funcoes_do_recorte(views_path):
        info = arquivo["functions"][nome]
        s = info["summary"]
        linha = {
            "comandos": s["num_statements"], "comandos_cobertos": s["covered_lines"],
            "desvios": s["num_branches"], "desvios_cobertos": s["covered_branches"],
            "linhas_nao_cobertas": info["missing_lines"],
            "desvios_nao_cobertos": info.get("missing_branches", []),
        }
        por_funcao[nome] = linha
        for chave in total:
            total[chave] += linha[chave]
    total["pct_comandos"] = round(100 * total["comandos_cobertos"] / total["comandos"], 1)
    total["pct_desvios"] = round(100 * total["desvios_cobertos"] / total["desvios"], 1) if total["desvios"] else 100.0
    arquivo_total = arquivo["summary"]
    return {
        "recorte": total,
        "por_funcao": por_funcao,
        "views_py_inteiro": {
            "comandos": arquivo_total["num_statements"], "comandos_cobertos": arquivo_total["covered_lines"],
            "desvios": arquivo_total["num_branches"], "desvios_cobertos": arquivo_total["covered_branches"],
            "pct_total": round(arquivo_total["percent_covered"], 1),
        },
    }


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ETAPAS:
        raise SystemExit(f"Informe a etapa: {', '.join(ETAPAS)}")
    etapa = sys.argv[1]
    versao, marcas = ETAPAS[etapa]
    saida = ROOT / "evidencias" / etapa
    shutil.rmtree(saida, ignore_errors=True)
    saida.mkdir(parents=True)
    if versao == "original":
        extrair_original()
    views_path = ROOT / (".sut-original/hotel/views.py" if versao == "original" else "hotel/views.py")

    env = {**os.environ, "SUT_VERSAO": versao, "PYTHONIOENCODING": "utf-8"}
    comando = [
        str(PYTHON), "-m", "pytest", "-v", "-rxX", "-m", marcas,
        "--cov=hotel.views", "--cov-branch",
        "--cov-report=term-missing",
        f"--cov-report=json:{saida / 'coverage.json'}",
        f"--cov-report=html:{saida / 'htmlcov'}",
        f"--junitxml={saida / 'junit.xml'}",
        f"--rastreabilidade={saida / 'rastreabilidade.json'}",
    ]
    cabecalho = f"# Etapa: {etapa}\n# SUT: {versao}\n# Comando: SUT_VERSAO={versao} {' '.join(comando[1:])}\n\n"
    processo = subprocess.run(comando, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")
    (saida / "pytest.txt").write_text(cabecalho + processo.stdout + processo.stderr, encoding="utf-8")
    print(processo.stdout[-2500:])

    resumo = cobertura_do_recorte(saida / "coverage.json", views_path)
    resumo["etapa"] = etapa
    resumo["sut"] = versao
    resumo["marcas"] = marcas
    resumo["casos"] = len(json.loads((saida / "rastreabilidade.json").read_text(encoding="utf-8")))
    (saida / "cobertura-recorte.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumo["recorte"], ensure_ascii=False))
    print(json.dumps({k: (v["linhas_nao_cobertas"], v["desvios_nao_cobertos"]) for k, v in resumo["por_funcao"].items()}))
    # Na versão original, falhas esperadas (xfail estrito) não geram código de erro.
    sys.exit(processo.returncode)


if __name__ == "__main__":
    main()
