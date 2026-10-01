"""Monta o relatório técnico a partir do modelo e das evidências e gera HTML e PDF.

Uso (na raiz do repositório, depois de etapas.ps1 e capturar_telas.py):

    uv run --with markdown==3.9 --with playwright==1.55.0 python scripts/gerar_relatorio.py

Os números de cobertura, mutação e evolução são lidos de evidencias/, para
que o relatório fique sempre coerente com as execuções registradas.
Saídas: docs/RELATORIO_TECNICO.md, docs/relatorio-tecnico.html, docs/relatorio-tecnico.pdf.
"""

import json
from pathlib import Path
import re

import markdown
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVID = ROOT / "evidencias"
FORK_URL = "https://github.com/gabrielfjm/Hotel_Management_System"

TELAS = [
    ("original-01-inicio", "Página inicial do sistema original em execução (Flask, porta local)."),
    ("original-03-quartos", "Lista de quartos após o login de Ana (código original)."),
    ("original-05-consulta-resultado", "Consulta de D+20 a D+22 para 4 hóspedes no original: o 101, livre nesse "
                                        "período, não aparece (DEF-01), e o 102, com capacidade 3, aparece (DEF-14)."),
    ("corrigida-05-consulta-resultado", "Mesma consulta no código corrigido: só o 103 comporta 4 hóspedes."),
    ("original-07-reserva-resultado", "Reserva do 101 em D+20 a D+22 recusada no original, embora o quarto só "
                                      "esteja ocupado de D+10 a D+12 (DEF-01)."),
    ("corrigida-07-reserva-resultado", "Mesma reserva aceita no código corrigido."),
    ("corrigida-08-minha-conta", "“My Account” no código corrigido: reservas, custos e o botão de cancelamento via POST."),
]


def ler(nome):
    return json.loads((EVID / nome).read_text(encoding="utf-8"))


def pct(valor):
    return f"{valor:.1f}%".replace(".", ",")


def main():
    texto = (DOCS / "partes" / "relatorio_modelo.md").read_text(encoding="utf-8")
    evolucao = ler("evolucao.json")
    final = ler("final-corrigida/cobertura-recorte.json")
    mut_ini = ler("mutacao-inicial/resumo.json")
    mut_fim = ler("mutacao-final/resumo.json")
    equivalentes = 7  # S8 a S14, classificados na seção 7.2 do relatório
    casos_mutacao = 6
    vivos_nao_equiv = mut_fim["sobreviventes"] - equivalentes

    linhas = ["| Etapa | Técnica | Código | Nº de casos | Passaram | Falharam (defeito confirmado) | Cobertura de comandos | "
              "Cobertura de desvios | Escore de mutação |", "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for e in evolucao:
        escore = f'{e["mutacao"]} ({pct(e["escore_pct"])})' if e["escore_pct"] is not None else "—"
        linhas.append(f'| {e["etapa"]} | {e["tecnica"]} | {e["sut"]} | {e["casos"]} | {e["passaram"]} | {e["xfail"]} | '
                      f'{e["comandos"]} ({pct(e["pct_comandos"])}) | {e["desvios"]} ({pct(e["pct_desvios"])}) | {escore} |')
    linhas.append("")
    linhas.append("Na linha 3, o escore é o da rodada **inicial** do Cosmic Ray, executada com a suíte funcional + "
                  "estrutural sobre o código corrigido. Na linha 4, é o da rodada **final**, com a suíte completa. "
                  "Nas etapas 1 e 2 não há escore, pois a mutação só é aplicada depois da correção dos defeitos (seção 6). "
                  "Fonte: `evidencias/evolucao.json`, gerado por `scripts/evolucao.py`.")

    nomes = {"1. Funcional": ("1", "Funcional (classes de equivalência + valor limite)"),
             "2. Estrutural": ("2", "Estrutural (meta: 100% de comandos e de desvios viáveis)"),
             "3. Correção": ("—", "Correção dos defeitos; mesma suíte"),
             "4. Mutação": ("3", "Baseada em defeitos (Cosmic Ray)")}
    resumo = ["| Etapa | Técnica | Código | Nº de casos | Cobertura de comandos | Cobertura de desvios | Escore de mutação |",
              "|---|---|---|---:|---:|---:|---:|"]
    for e in evolucao:
        num, tec = nomes[e["etapa"]]
        escore = f'{e["mutacao"]} ({pct(e["escore_pct"])})' if e["escore_pct"] is not None else "—"
        resumo.append(f'| {num} | {tec} | {e["sut"]} | {e["casos"]} | {e["comandos"]} ({pct(e["pct_comandos"])}) | '
                      f'{e["desvios"]} ({pct(e["pct_desvios"])}) | {escore} |')

    nomes_req = {"REQ-01": "REQ-01 Reservar quartos", "REQ-02": "REQ-02 Data de entrada",
                 "REQ-03": "REQ-03 Data de saída"}
    catalogo = json.loads((ROOT / "tests" / "classes_equivalencia.json").read_text(encoding="utf-8"))
    tabela_ce = ["| Req. | Condição de entrada | Classes válidas | Classes inválidas |", "|---|---|---|---|"]
    for req, nome_req in nomes_req.items():
        condicoes = list(dict.fromkeys(c["condicao"] for c in catalogo if c["req"] == req))
        for i, cond in enumerate(condicoes):
            grupo = [c for c in catalogo if c["req"] == req and c["condicao"] == cond]
            validas = "; ".join(f'{c["id"]} {c["descricao"]}' for c in grupo if c["tipo"] == "válida") or "—"
            invalidas = "; ".join(f'{c["id"]} {c["descricao"]}' for c in grupo if c["tipo"] == "inválida") or "—"
            tabela_ce.append(f'| {nome_req if i == 0 else ""} | {cond} | {validas} | {invalidas} |')

    telas = []
    for nome, legenda in TELAS:
        if (EVID / "telas" / f"{nome}.png").exists():
            telas.append(f"![{legenda}](../evidencias/telas/{nome}.png)\n\n*{legenda}*\n")
    rastreab = (EVID / "rastreabilidade.md").read_text(encoding="utf-8").split("\n\n")[1]

    trocas = {
        "«FORK_URL»": FORK_URL,
        "«RESUMO»": "\n".join(resumo),
        "«TABELA_CE»": "\n".join(tabela_ce),
        "«CASOS_SECUNDARIOS»": (DOCS / "partes" / "casos_secundarios.md").read_text(encoding="utf-8"),
        "«ORIG_CMD»": str(ler("funcional-original/cobertura-recorte.json")["recorte"]["comandos"]),
        "«ORIG_DESV»": str(ler("funcional-original/cobertura-recorte.json")["recorte"]["desvios"]),
        "«MUT_TOTAL»": str(mut_fim["total"]),
        "«TELAS»": "\n".join(telas),
        "«CASOS_FUNCIONAIS»": (DOCS / "partes" / "casos_funcionais.md").read_text(encoding="utf-8"),
        "«DEFEITOS»": (DOCS / "partes" / "defeitos.md").read_text(encoding="utf-8"),
        "«EVOLUCAO»": "\n".join(linhas),
        "«RASTREABILIDADE»": rastreab,
        "«COV_FINAL_CMD»": f'{final["recorte"]["comandos_cobertos"]}/{final["recorte"]["comandos"]} ({pct(final["recorte"]["pct_comandos"])})',
        "«COV_FINAL_DESV»": f'{final["recorte"]["desvios_cobertos"]}/{final["recorte"]["desvios"]} ({pct(final["recorte"]["pct_desvios"])})',
        "«COV_VIEWS_TOTAL»": pct(final["views_py_inteiro"]["pct_total"]),
        "«MUT_FINAL»": f'{mut_fim["mortos"]}/{mut_fim["total"]} ({pct(mut_fim["escore_pct"])})',
        "«MUT_FINAL_TEXTO»": (
            f'{mut_fim["total"]} mutantes: {mut_fim["mortos"]} mortos, {mut_fim["sobreviventes"]} sobreviventes, '
            f'{mut_fim["incompetentes"]} incompetentes. Escore de {pct(mut_fim["escore_pct"])} '
            f'(inicial: {pct(mut_ini["escore_pct"])}), em {mut_fim["duracao_s"]:.0f} s.** Os {casos_mutacao} casos novos '
            f'mataram os {mut_ini["sobreviventes"] - equivalentes} sobreviventes não equivalentes. Restam {mut_fim["sobreviventes"]} sobreviventes, '
            f'todos classificados como equivalentes (S8 a S14); não equivalentes restantes: {vivos_nao_equiv}. '
            f'O arquivo `evidencias/mutacao-final/sobreviventes.txt` traz o diff de cada um.'),
        "«MUT_AJUSTADO»": pct(100 * mut_fim["mortos"] / (mut_fim["total"] - equivalentes)) +
                          f' ({mut_fim["mortos"]}/{mut_fim["total"] - equivalentes})',
    }
    for chave, valor in trocas.items():
        texto = texto.replace(chave, valor)
    faltando = re.findall(r"«[A-Z_]+»", texto)
    if faltando:
        raise SystemExit(f"Marcadores não preenchidos: {faltando}")
    (DOCS / "RELATORIO_TECNICO.md").write_text(texto, encoding="utf-8")

    corpo = markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists"])
    html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Relatório técnico – Hotel Management System</title>
<style>
@page {{ size: A4; margin: 16mm 14mm; }}
body {{ font-family: "Segoe UI", Calibri, Arial, sans-serif; font-size: 10pt; line-height: 1.45; color: #1d1d1f; }}
h1 {{ font-size: 19pt; color: #7a0c2e; border-bottom: 2px solid #7a0c2e; padding-bottom: 4px; }}
h2 {{ font-size: 14pt; color: #0f2a4a; margin-top: 22px; border-bottom: 1px solid #c8cfd8; padding-bottom: 2px; }}
h3 {{ font-size: 11.5pt; color: #0f2a4a; }}
table {{ border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 8.3pt; page-break-inside: auto; }}
tr {{ page-break-inside: avoid; }}
th {{ background: #0f2a4a; color: #fff; text-align: left; padding: 4px 5px; }}
td {{ border: 1px solid #c8cfd8; padding: 3px 5px; vertical-align: top; }}
tr:nth-child(even) td {{ background: #f4f6f9; }}
code {{ font-family: Consolas, monospace; font-size: 8.6pt; background: #eef1f5; padding: 0 2px; border-radius: 2px; }}
pre {{ background: #eef1f5; padding: 8px; font-size: 8.5pt; white-space: pre-wrap; }}
img {{ max-width: 62%; display: block; margin: 8px auto 2px; border: 1px solid #c8cfd8; }}
p > em:only-child {{ display: block; text-align: center; font-size: 8.5pt; color: #555; }}
</style></head><body>{corpo}</body></html>"""
    destino_html = DOCS / "relatorio-tecnico.html"
    destino_html.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge")
        pagina = navegador.new_page()
        pagina.goto(destino_html.resolve().as_uri())
        pagina.pdf(path=str(DOCS / "relatorio-tecnico.pdf"), format="A4", print_background=True,
                   display_header_footer=True, header_template="<span></span>",
                   footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#666">'
                                   '<span class="pageNumber"></span> / <span class="totalPages"></span></div>',
                   margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"})
        navegador.close()
    print(f"Relatório: {DOCS / 'relatorio-tecnico.pdf'}")


if __name__ == "__main__":
    main()
