# Evidências de execução

Geradas por `etapas.ps1` (e pelos scripts citados). Os números batem com o relatório técnico, que é montado a partir destes arquivos.

| Pasta / arquivo | Etapa | Código testado | Casos | Resultado | Cobertura do recorte (comandos / desvios) |
|---|---|---|---:|---|---|
| `metricas/` | Caracterização | upstream `71b396b` | — | radon raw/cc e pygount: 5 módulos, 428 LOC, 354 SLOC, 12 classes, 13 funções + 6 métodos | — |
| `telas/` | Execução do sistema | original e corrigido | — | capturas do navegador (Edge) | — |
| `telas-vvtestlab/` | Gestão dos testes | — | — | capturas do V&V TestLab com o estudo carregado | — |
| `funcional-original/` | 1. Funcional | original | 15 | 6 passaram, 9 xfail (defeitos) | 60/63 (95,2%) / 29/34 (85,3%) |
| `estrutural-original/` | 2. Estrutural | original | 19 | 9 passaram, 10 xfail | 63/63 (100%) / 33/34 (97,1%) |
| `correcoes.diff` | Correção | original → corrigido | — | `git diff sut-original sut-corrigido -- hotel` | — |
| `suite-corrigida/` | Correção (base da mutação) | corrigido | 19 | 19 passaram | 65/65 (100%) / 28/28 (100%) |
| `mutacao-inicial/` | 3. Mutação, rodada inicial | corrigido | 19 | 141 mutantes: 127 mortos, 14 sobreviventes (90,1%) | — |
| `mutacao-final/` | 3. Mutação, rodada final | corrigido | 25 | 141 mutantes: 134 mortos, 7 sobreviventes equivalentes (95,0%) | — |
| `final-corrigida/` | Suíte final | corrigido | 25 | 25 passaram | 65/65 (100%) / 28/28 (100%) |
| `secundarios-original/` | Complementares (RF-04 e RF-08, fora das métricas) | original | 14 | 3 passaram, 11 xfail (DEF-07 a DEF-17) | — |
| `secundarios-corrigida/` | Complementares (RF-04 e RF-08, fora das métricas) | corrigido | 14 | 14 passaram | — |
| `evolucao.json` | Consolidação | — | — | tabela de evolução por etapa | — |
| `rastreabilidade.md` | Consolidação | — | — | classe → casos e caso → defeito | — |

Conteúdo de cada pasta de etapa: `pytest.txt` (comando, saída `-v -rxX` e `term-missing`), `junit.xml`, `coverage.json`, `htmlcov/index.html`, `rastreabilidade.json` e `cobertura-recorte.json`.

Conteúdo de cada pasta de mutação:

* `cosmic-ray.toml`: configuração efetiva.
* `sessao.sqlite`: sessão do Cosmic Ray, inspecionável com `cosmic-ray dump` ou `cr-report`.
* `resumo.json`: totais por função e por operador.
* `sobreviventes.txt`: diff de cada sobrevivente.
* `execucao.txt`: comando e duração.
