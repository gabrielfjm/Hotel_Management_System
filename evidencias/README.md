# Evidências de execução

Geradas por `etapas.ps1` (e pelos scripts citados). Os números batem com o relatório técnico, que é montado a partir destes arquivos.

| Pasta / arquivo | Etapa | Código testado | Casos | Resultado | Cobertura do recorte (comandos / desvios) |
|---|---|---|---:|---|---|
| `metricas/` | Caracterização | upstream `71b396b` | — | radon raw/cc e pygount: 5 módulos, 428 LOC, 354 SLOC, 12 classes, 13 funções + 6 métodos | — |
| `telas/` | Execução do sistema | original e corrigido | — | capturas do navegador (Edge) | — |
| `telas-vvtestlab/` | Gestão dos testes | — | — | capturas do V&V TestLab com o estudo carregado | — |
| `funcional-original/` | 1. Funcional | original | 52 | 22 passaram, 30 xfail (defeitos) | 93/103 (90,3%) / 45/54 (83,3%) |
| `estrutural-original/` | 2. Estrutural | original | 59 | 26 passaram, 33 xfail | 103/103 (100%) / 53/54 (98,1%) |
| `correcoes.diff` | Correção | original → corrigido | — | `git diff sut-original sut-corrigido -- hotel` | — |
| `suite-corrigida/` | Correção (base da mutação) | corrigido | 59 | 59 passaram | 106/106 (100%) / 44/44 (100%) |
| `mutacao-inicial/` | 3. Mutação, rodada inicial | corrigido | 59 | 204 mutantes: 191 mortos, 13 sobreviventes (93,6%) | — |
| `mutacao-final/` | 3. Mutação, rodada final | corrigido | 64 | 204 mutantes: 196 mortos, 8 sobreviventes equivalentes (96,1%) | — |
| `final-corrigida/` | Suíte final | corrigido | 64 | 64 passaram | 106/106 (100%) / 44/44 (100%) |
| `evolucao.json` | Consolidação | — | — | tabela de evolução por etapa | — |
| `rastreabilidade.md` | Consolidação | — | — | classe → casos e caso → defeito | — |

Conteúdo de cada pasta de etapa: `pytest.txt` (comando, saída `-v -rxX` e `term-missing`), `junit.xml`, `coverage.json`, `htmlcov/index.html`, `rastreabilidade.json` e `cobertura-recorte.json`.

Conteúdo de cada pasta de mutação:

* `cosmic-ray.toml`: configuração efetiva.
* `sessao.sqlite`: sessão do Cosmic Ray, inspecionável com `cosmic-ray dump` ou `cr-report`.
* `resumo.json`: totais por função e por operador.
* `sobreviventes.txt`: diff de cada sobrevivente.
* `execucao.txt`: comando e duração.
