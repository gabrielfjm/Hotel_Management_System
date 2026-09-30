"""Métricas de código do SUT original com radon e pygount.

Mede o commit do upstream (tag upstream-71b396b) extraído com git archive, para
excluir da contagem tudo o que não é código de produção do projeto: testes,
scripts e infraestrutura desta análise, ambientes virtuais (.venv*) e as
bibliotecas de front-end vendorizadas (hotel/static/bootstrap). Apenas os
arquivos .py do projeto entram (app.py e o pacote hotel/).

Requer uv (usa "uvx radon" e "uvx pygount"). Uso, na raiz do repositório:

    python scripts/metricas_codigo.py

Saídas em evidencias/metricas/: radon-raw.txt, radon-cc.txt, radon-cc.json,
pygount.txt e metricas.json (resumo).
"""

import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "evidencias" / "metricas"
TAG = "upstream-71b396b"
ALVOS = ["app.py", "hotel"]
RADON = "radon==6.0.1"
PYGOUNT = "pygount==3.1.0"


def rodar(comando, cwd):
    processo = subprocess.run(comando, cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=True)
    return processo.stdout


def main():
    shutil.rmtree(SAIDA, ignore_errors=True)
    SAIDA.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as pasta:
        pasta = Path(pasta)
        arquivo = subprocess.run(["git", "archive", "--format=tar", TAG], cwd=ROOT, check=True,
                                 capture_output=True).stdout
        with tarfile.open(fileobj=io.BytesIO(arquivo)) as tar:
            tar.extractall(pasta, filter="data")
        modulos = sorted(str(p.relative_to(pasta)).replace("\\", "/") for p in pasta.rglob("*.py"))

        comandos = {
            "radon-raw.txt": ["uvx", RADON, "raw", "-s", *ALVOS],
            "radon-cc.txt": ["uvx", RADON, "cc", "-s", "-a", "--total-average", *ALVOS],
            "radon-cc.json": ["uvx", RADON, "cc", "-j", *ALVOS],
            "pygount.txt": ["uvx", PYGOUNT, "--format=summary", "--suffix=py", *ALVOS],
        }
        saidas = {}
        for nome, comando in comandos.items():
            saidas[nome] = rodar(comando, pasta)
            cabecalho = "" if nome.endswith(".json") else f"# Código: {TAG}\n# Comando: {' '.join(comando[1:] if comando[0] == 'uvx' else comando)}\n\n"
            (SAIDA / nome).write_text(cabecalho + saidas[nome], encoding="utf-8")

        raw_json = json.loads(rodar(["uvx", RADON, "raw", "-j", *ALVOS], pasta))

    blocos = json.loads(saidas["radon-cc.json"])
    classes, funcoes, metodos = set(), 0, 0
    complexidades = []
    for arquivo, itens in blocos.items():
        for bloco in itens:
            if bloco["type"] == "class":
                classes.add((arquivo, bloco["name"]))
                for m in bloco.get("methods", []):
                    metodos += 1
                    complexidades.append(m["complexity"])
            elif bloco["type"] == "function":
                funcoes += 1
                complexidades.append(bloco["complexity"])
            elif bloco["type"] == "method":
                pass  # já contados via "methods" da classe
    total = {chave: sum(v[chave] for v in raw_json.values()) for chave in ("loc", "lloc", "sloc", "comments", "blank")}
    resumo = {
        "codigo": TAG,
        "ferramentas": {"radon": RADON, "pygount": PYGOUNT},
        "modulos": modulos,
        "num_modulos": len(modulos),
        "loc_fisico": total["loc"],
        "sloc": total["sloc"],
        "lloc": total["lloc"],
        "comentarios": total["comments"],
        "linhas_em_branco": total["blank"],
        "classes": len(classes),
        "funcoes": funcoes,
        "metodos": metodos,
        "funcoes_mais_metodos": funcoes + metodos,
        "complexidade_ciclomatica_media": round(sum(complexidades) / len(complexidades), 2),
        "complexidade_ciclomatica_max": max(complexidades),
        "por_modulo": {k.replace("\\", "/"): {"loc": v["loc"], "sloc": v["sloc"], "lloc": v["lloc"]}
                       for k, v in raw_json.items()},
    }
    (SAIDA / "metricas.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in resumo.items() if k != "por_modulo"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
