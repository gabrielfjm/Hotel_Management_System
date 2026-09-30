"""Consolida as evidências em tabelas: evolução por etapa e rastreabilidade.

Lê evidencias/<etapa>/{junit.xml, cobertura-recorte.json, rastreabilidade.json}
e evidencias/mutacao-*/resumo.json. Verifica que toda classe de equivalência de
tests/classes_equivalencia.json é exercitada por ao menos um caso funcional.
Grava evidencias/evolucao.json e evidencias/rastreabilidade.md.
"""

from collections import defaultdict
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidencias"


def ler(caminho):
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else None


def contagem_junit(caminho):
    raiz = ET.parse(caminho).getroot()
    suite = raiz if raiz.tag == "testsuite" else raiz.find("testsuite")
    total = int(suite.get("tests"))
    pulados = int(suite.get("skipped"))  # xfail aparece como skipped no JUnit
    falhas = int(suite.get("failures")) + int(suite.get("errors"))
    return {"casos": total, "passaram": total - pulados - falhas, "xfail": pulados, "falharam": falhas}


def main():
    etapas = [
        ("1. Funcional", "Classes de equivalência + valor limite", "funcional-original", None),
        ("2. Estrutural", "Cobertura de comandos e desvios", "estrutural-original", None),
        ("3. Correção", "Suíte funcional + estrutural no código corrigido", "suite-corrigida", "inicial"),
        ("4. Mutação", "Casos para matar mutantes sobreviventes", "final-corrigida", "final"),
    ]
    linhas = []
    for nome, tecnica, pasta, rodada in etapas:
        cobertura = ler(EVID / pasta / "cobertura-recorte.json")
        if cobertura is None:
            continue
        mut = ler(EVID / f"mutacao-{rodada}" / "resumo.json") if rodada else None
        linhas.append({
            "etapa": nome, "tecnica": tecnica, "evidencia": pasta, "sut": cobertura["sut"],
            **contagem_junit(EVID / pasta / "junit.xml"),
            "comandos": f'{cobertura["recorte"]["comandos_cobertos"]}/{cobertura["recorte"]["comandos"]}',
            "pct_comandos": cobertura["recorte"]["pct_comandos"],
            "desvios": f'{cobertura["recorte"]["desvios_cobertos"]}/{cobertura["recorte"]["desvios"]}',
            "pct_desvios": cobertura["recorte"]["pct_desvios"],
            "views_py_total_pct": cobertura["views_py_inteiro"]["pct_total"],
            "mutacao": (f'{mut["mortos"]}/{mut["mortos"] + mut["sobreviventes"]}' if mut else "—"),
            "escore_pct": mut["escore_pct"] if mut else None,
        })
    (EVID / "evolucao.json").write_text(json.dumps(linhas, ensure_ascii=False, indent=2), encoding="utf-8")

    classes = ler(ROOT / "tests" / "classes_equivalencia.json")
    matriz = ler(EVID / "final-corrigida" / "rastreabilidade.json") or []
    por_classe = defaultdict(list)
    for caso in matriz:
        for ce in caso["classes"]:
            por_classe[ce].append((caso["caso"], caso["etapa"]))
    faltando = [c["id"] for c in classes if not any(etapa == "funcional" for _, etapa in por_classe[c["id"]])]
    desconhecidas = sorted(set(por_classe) - {c["id"] for c in classes})

    md = ["# Rastreabilidade: classe de equivalência → casos de teste", "",
          "| Classe | Req. | Condição | Tipo | Descrição | Casos funcionais | Outros casos |",
          "|---|---|---|---|---|---|---|"]
    for c in classes:
        func = ", ".join(n for n, e in por_classe[c["id"]] if e == "funcional")
        outros = ", ".join(n for n, e in por_classe[c["id"]] if e != "funcional") or "—"
        md.append(f'| {c["id"]} | {c["req"]} | {c["condicao"]} | {c["tipo"]} | {c["descricao"]} | {func} | {outros} |')
    md += ["", "| Caso | Etapa | Classes | Defeito revelado no original |", "|---|---|---|---|"]
    for caso in sorted(matriz, key=lambda c: c["caso"]):
        md.append(f'| {caso["caso"]} | {caso["etapa"]} | {", ".join(caso["classes"])} | {caso["defeito"] or "—"} |')
    (EVID / "rastreabilidade.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    for linha in linhas:
        print(f'{linha["etapa"]:<14} {linha["casos"]:>3} casos  cmd {linha["pct_comandos"]:>5}%  '
              f'desv {linha["pct_desvios"]:>5}%  mutação {linha["mutacao"]} ({linha["escore_pct"]})')
    print(f"Classes sem caso funcional: {faltando or 'nenhuma'}; IDs desconhecidos: {desconhecidas or 'nenhum'}")
    if faltando or desconhecidas:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
