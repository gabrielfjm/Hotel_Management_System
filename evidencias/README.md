# Evidências de execução

Geradas por `etapas.ps1` (e pelos scripts citados). Os números batem com o relatório técnico, que é montado a partir destes arquivos.

| Pasta / arquivo | Etapa | Código testado | Casos | Resultado | Cobertura do recorte (comandos / desvios) |
|---|---|---|---:|---|---|
| `metricas/` | Caracterização | upstream `71b396b` | — | radon raw/cc e pygount: 5 módulos, 428 LOC, 354 SLOC, 12 classes, 13 funções + 6 métodos | — |
| `telas/` | Execução do sistema | original e corrigido | — | capturas do navegador (Edge) | — |
| `telas-vvtestlab/` | Gestão dos testes | — | — | capturas do V&V TestLab com o estudo carregado | — |
| `funcional-original/` | 1. Funcional | original | 50 | 22 passaram, 28 xfail (defeitos) | 84/92 (91,3%) / 42/50 (84,0%) |
| `estrutural-original/` | 2. Estrutural | original | 57 | 26 passaram, 31 xfail | 92/92 (100%) / 49/50 (98,0%) |
| `correcoes.diff` | Correção | original → corrigido | — | `git diff sut-original sut-corrigido -- hotel` | — |
| `suite-corrigida/` | Correção (base da mutação) | corrigido | 57 | 57 passaram | 92/92 (100%) / 38/38 (100%) |
| `mutacao-inicial/` | 3. Mutação, rodada inicial | corrigido | 57 | 189 mutantes: 178 mortos, 11 sobreviventes (94,2%) | — |
| `mutacao-final/` | 3. Mutação, rodada final | corrigido | 60 | 189 mutantes: 181 mortos, 8 sobreviventes equivalentes (95,8%) | — |
| `final-corrigida/` | Suíte final | corrigido | 60 | 60 passaram | 92/92 (100%) / 38/38 (100%) |
| `secundarios-original/` | Complementares (RF-08, fora das métricas) | original | 8 | 2 passaram, 6 xfail (DEF-07 a DEF-11) | — |
| `secundarios-corrigida/` | Complementares (RF-08, fora das métricas) | corrigido | 8 | 8 passaram | — |
| `evolucao.json` | Consolidação | — | — | tabela de evolução por etapa | — |
| `rastreabilidade.md` | Consolidação | — | — | classe → casos e caso → defeito | — |

Conteúdo de cada pasta de etapa: `pytest.txt` (comando, saída `-v -rxX` e `term-missing`), `junit.xml`, `coverage.json`, `htmlcov/index.html`, `rastreabilidade.json` e `cobertura-recorte.json`.

Conteúdo de cada pasta de mutação:

* `cosmic-ray.toml`: configuração efetiva.
* `sessao.sqlite`: sessão do Cosmic Ray, inspecionável com `cosmic-ray dump` ou `cr-report`.
* `resumo.json`: totais por função e por operador.
* `sobreviventes.txt`: diff de cada sobrevivente.
* `execucao.txt`: comando e duração.
