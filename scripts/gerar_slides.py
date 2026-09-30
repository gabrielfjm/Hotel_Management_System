"""Gera a apresentação de 2 slides a partir das evidências.

Uso: uv run --no-project --python 3.12 --with python-pptx==1.0.2 python scripts/gerar_slides.py
Saída: docs/apresentacao-2-slides.pptx
"""

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidencias"
VINHO = RGBColor(0x7A, 0x0C, 0x2E)
AZUL = RGBColor(0x0F, 0x2A, 0x4A)
CINZA = RGBColor(0x55, 0x5B, 0x66)
CLARO = RGBColor(0xF2, 0xF4, 0xF7)
BRANCO = RGBColor(0xFF, 0xFF, 0xFF)


def caixa(slide, x, y, w, h, fundo=None):
    forma = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    forma.line.fill.background()
    if fundo is None:
        forma.fill.background()
    else:
        forma.fill.solid()
        forma.fill.fore_color.rgb = fundo
    forma.shadow.inherit = False
    tf = forma.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = Inches(0.12)
    tf.margin_top = tf.margin_bottom = Inches(0.06)
    return tf


def paragrafo(tf, texto, tamanho=12, cor=AZUL, negrito=False, primeiro=False, espaco=3):
    p = tf.paragraphs[0] if primeiro else tf.add_paragraph()
    p.space_after = Pt(espaco)
    p.alignment = PP_ALIGN.LEFT
    partes = texto.split("**")
    for i, parte in enumerate(partes):
        if not parte:
            continue
        r = p.add_run()
        r.text = parte
        r.font.size = Pt(tamanho)
        r.font.color.rgb = cor
        r.font.bold = negrito or i % 2 == 1
        r.font.name = "Segoe UI"
    return p


def titulo(slide, texto, subtitulo):
    tf = caixa(slide, 0.4, 0.25, 12.5, 0.6)
    paragrafo(tf, texto, 26, VINHO, True, primeiro=True)
    tf2 = caixa(slide, 0.4, 0.85, 12.5, 0.4)
    paragrafo(tf2, subtitulo, 13, CINZA, primeiro=True)
    linha = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.28), Inches(12.3), Inches(0.04))
    linha.fill.solid()
    linha.fill.fore_color.rgb = VINHO
    linha.line.fill.background()


def slide_processo(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    titulo(s, "1. Processo de desenvolvimento do teste",
           "Hotel Management System (Flask/SQLite, 354 SLOC) · commit 71b396b · "
           "recorte: reservar, cancelar e consultar disponibilidade")
    etapas = [
        ("1  Funcional", "pytest · só a especificação",
         ["22 condições → **48 classes** (31 válidas, 17 inválidas)",
          "Valor limite: abaixo / no limite / acima (datas, noites, hóspedes, capacidade, adjacência)",
          "**47 casos**; 1 classe inválida por caso",
          "Original: 21 passam, **26 falham → 16 defeitos**"]),
        ("2  Estrutural", "coverage.py --branch",
         ["Meta: **100% comandos e desvios viáveis** nas 5 funções",
          "Lacunas da etapa 1 → +7 casos (sessão encerrada, GET, outros quartos)",
          "Leitura do código revela **+3 defeitos** (estado global, remove no laço, produto cartesiano)",
          "**54 casos**: 100% comandos, 98,1% desvios (1 inviável)"]),
        ("Correção", "fork no GitHub · 6 commits",
         ["19 defeitos corrigidos, 1 commit por grupo, cada um confirmado pelo teste que o revelou",
          "Mesmo teste: xfail estrito no original, verde no corrigido",
          "**54/54 passam**, sem skip; 100% comandos e desvios"]),
        ("3  Mutação", "Cosmic Ray 8.4.3 · sem amostragem",
         ["**204 mutantes** (todos os operadores, funções do recorte)",
          "Inicial: 191 mortos → **93,6%**",
          "13 sobreviventes: 5 matáveis → +5 casos; 8 equivalentes justificados",
          "Final: 196 mortos → **96,1%** (100% dos não equivalentes)"]),
    ]
    x = 0.45
    for nome, ferramenta, itens in etapas:
        cab = caixa(s, x, 1.55, 3.0, 0.75, AZUL if nome != "Correção" else VINHO)
        paragrafo(cab, nome, 17, BRANCO, True, primeiro=True, espaco=0)
        paragrafo(cab, ferramenta, 10.5, BRANCO, espaco=0)
        corpo = caixa(s, x, 2.3, 3.0, 3.35, CLARO)
        for i, item in enumerate(itens):
            paragrafo(corpo, "• " + item, 11.5, AZUL, primeiro=(i == 0), espaco=6)
        x += 3.12
    rodape = caixa(s, 0.45, 5.85, 12.4, 1.35)
    paragrafo(rodape, "**Rastreabilidade:** REQ → CE (@pytest.mark.ce) → CT (nome do teste) → DEF (@pytest.mark.defeito) → "
              "commit de correção. Um script verifica que toda classe tem caso funcional.", 12, AZUL, primeiro=True)
    paragrafo(rodape, "**Reprodutível:** SUT_VERSAO=original|corrigida escolhe o código; etapas.ps1 roda tudo e grava "
              "pytest.txt, junit.xml, coverage JSON/HTML e sessões Cosmic Ray em evidencias/.", 12, AZUL)


def slide_resultados(prs, evolucao):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    titulo(s, "2. Resultados, dificuldades e lições aprendidas",
           "19 defeitos encontrados e corrigidos · suíte final: 59 casos, 100% de desvios, 96,1% de escore de mutação")
    linhas, colunas = len(evolucao) + 1, 6
    tabela = s.shapes.add_table(linhas, colunas, Inches(0.45), Inches(1.5), Inches(7.3), Inches(1.9)).table
    cab = ["Etapa", "Código", "Casos", "Comandos", "Desvios", "Mutação"]
    larguras = [1.55, 1.05, 0.8, 1.25, 1.25, 1.4]
    for j, (texto, largura) in enumerate(zip(cab, larguras)):
        tabela.columns[j].width = Inches(largura)
        c = tabela.cell(0, j)
        c.text = texto
        c.fill.solid()
        c.fill.fore_color.rgb = AZUL
    for i, e in enumerate(evolucao, start=1):
        valores = [e["etapa"], e["sut"], str(e["casos"]), f'{e["pct_comandos"]:.1f}%'.replace(".", ","),
                   f'{e["pct_desvios"]:.1f}%'.replace(".", ","),
                   f'{e["escore_pct"]:.1f}%'.replace(".", ",") if e["escore_pct"] is not None else "—"]
        for j, v in enumerate(valores):
            c = tabela.cell(i, j)
            c.text = v
            c.fill.solid()
            c.fill.fore_color.rgb = CLARO if i % 2 else BRANCO
    for i in range(linhas):
        for j in range(colunas):
            for p in tabela.cell(i, j).text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(11.5)
                    r.font.name = "Segoe UI"
                    r.font.bold = i == 0
                    r.font.color.rgb = BRANCO if i == 0 else AZUL

    defeitos = caixa(s, 0.45, 3.55, 7.3, 3.6)
    paragrafo(defeitos, "Defeitos mais graves (todos com teste automatizado)", 14, VINHO, True, primeiro=True)
    for item in [
        "**DEF-01** predicado de conflito é uma **tautologia**: depois da 1ª reserva, o quarto nunca mais fica livre",
        "**DEF-08/10** qualquer usuário cancela reserva alheia; **GET** apaga dados",
        "**DEF-15** produto cartesiano reservas × vínculos, **mascarado** pelo DEF-01",
        "**DEF-16/17** filtro em variável global vaza entre sessões; remove() no laço pula quartos",
        "Outros: entrada hoje recusada, 0 hóspedes aceito, quarto repetido/inexistente, KeyError/500 sem sessão",
    ]:
        paragrafo(defeitos, "• " + item, 11.5, AZUL, espaco=5)

    licoes = caixa(s, 8.0, 1.5, 4.9, 4.85, CLARO)
    paragrafo(licoes, "Lições aprendidas", 14, VINHO, True, primeiro=True)
    for item in [
        "**Funcional** achou 16 de 19 defeitos: limites (entrada hoje, estadias adjacentes) valem mais que valores típicos",
        "**Cobertura ≠ correção:** 100% dos comandos no original com 29 testes falhando",
        "**Estrutural** achou o que a especificação não sugere e revelou um defeito **mascarado**",
        "**Mutação testa os testes:** com 100% de desvios, 5 mutantes vivos (IDs > 256, oráculo de um sentido só)",
        "**Corrigir antes de mutar:** mutar o original invalidaria o escore",
    ]:
        paragrafo(licoes, "• " + item, 11.5, AZUL, espaco=6)
    paragrafo(licoes, "Dificuldades", 14, VINHO, True, espaco=3)
    for item in [
        "Dependências de 2019 → 2 ambientes (Py 3.9 / 3.12) e compat.py",
        "Cosmic Ray no Windows (caminho do interpretador)",
        "Oráculos não escritos → convenções declaradas no relatório",
    ]:
        paragrafo(licoes, "• " + item, 11.5, AZUL, espaco=4)


def main():
    evolucao = json.loads((EVID / "evolucao.json").read_text(encoding="utf-8"))
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    slide_processo(prs)
    slide_resultados(prs, evolucao)
    destino = ROOT / "docs" / "apresentacao-2-slides.pptx"
    prs.save(destino)
    print(destino)


if __name__ == "__main__":
    main()
