# Testes do Hotel Management System

Fork de [CrystalWang1225/Hotel_Management_System](https://github.com/CrystalWang1225/Hotel_Management_System) (commit `71b396b`) com testes funcionais, estruturais e de mutação e com a correção dos 19 defeitos encontrados. Relatório: [docs/relatorio-tecnico.pdf](docs/relatorio-tecnico.pdf) (fonte: [docs/RELATORIO_TECNICO.md](docs/RELATORIO_TECNICO.md)). Apresentação: [docs/apresentacao-2-slides.pptx](docs/apresentacao-2-slides.pptx) (com notas do apresentador) e slides de apoio à demonstração em [docs/apresentacao-apoio-demo.pptx](docs/apresentacao-apoio-demo.pptx).

## Tags

| Tag | Conteúdo |
|---|---|
| `upstream-71b396b` | código original da autora, sem alterações |
| `sut-original` | original + infraestrutura para executar (compat.py, URI do banco configurável); regras de negócio intactas |
| `sut-corrigido` | após os 6 commits de correção (`git diff sut-original sut-corrigido -- hotel`) |

## Requisitos

Windows (PowerShell) ou Linux/macOS (bash), [uv](https://docs.astral.sh/uv/) e git. Internet na primeira execução, para baixar Python 3.9/3.12 e os pacotes. As capturas de tela e o PDF usam o Microsoft Edge instalado.

## Passo a passo

```powershell
./setup_local.ps1        # .venv (Python 3.9: app, pytest, pytest-cov) e .venv-mutation (Python 3.12: Cosmic Ray)
./etapas.ps1             # tudo: métricas, etapas 1-2 no original, suíte corrigida, mutação inicial e final, suíte final (~10 min)
./etapas.ps1 -SemMutacao # só pytest + coverage (~30 s)
./executar.ps1           # sistema em http://127.0.0.1:5000 (ana@example.test / senha123)
```

Se a política do PowerShell bloquear scripts, use `powershell -ExecutionPolicy Bypass -File .\etapas.ps1`.

Linux/macOS: `./setup.sh`, `./etapas.sh` (ou `./etapas.sh --sem-mutacao`) e `./executar.sh`.

## Comandos individuais

```powershell
$py = '.venv/Scripts/python.exe'
& $py -m pytest -v                                        # suíte completa no código corrigido (64 passam)
$env:SUT_VERSAO='original'; & $py -m pytest -rxX          # no original: defeitos aparecem como xfail estrito
& $py -m pytest -m funcional --cov=hotel.views --cov-branch --cov-report=term-missing
& $py scripts/etapas.py funcional-original                # uma etapa, com evidências em evidencias/
.venv-mutation/Scripts/python.exe scripts/mutacao.py final
python scripts/metricas_codigo.py                         # radon + pygount (via uvx)
uv run --no-project --python 3.12 --with playwright==1.55.0 python scripts/capturar_telas.py
uv run --no-project --python 3.12 --with markdown==3.9 --with playwright==1.55.0 python scripts/gerar_relatorio.py
uv run --no-project --python 3.12 --with python-pptx==1.0.2 python scripts/gerar_slides.py
```

## Organização

| Caminho | Conteúdo |
|---|---|
| `tests/test_01_funcional.py` | CT-001 a CT-043, CT-051 a CT-054 e CT-060 a CT-064: classes de equivalência e valor limite |
| `tests/test_02_estrutural.py` | CT-044 a CT-050: casos guiados pela cobertura |
| `tests/test_03_mutacao.py` | CT-055 a CT-059: casos que matam mutantes sobreviventes |
| `tests/classes_equivalencia.json` | catálogo das 48 classes (CE-01 a CE-48) |
| `tests/conftest.py` | fixtures, escolha do SUT (`SUT_VERSAO`), marcas `ce`/`defeito`, exportação da rastreabilidade |
| `mutacao/*.toml` | configuração do Cosmic Ray por rodada |
| `scripts/` | `etapas.py`, `mutacao.py`, `metricas_codigo.py`, `evolucao.py`, `capturar_telas.py`, `gerar_relatorio.py`, `gerar_slides.py`, `seed_demo.py`, `inspecionar_base.py` |
| `evidencias/` | resultados de cada etapa; ver [evidencias/README.md](evidencias/README.md) |

## Marcas pytest

* `funcional`, `estrutural`, `mutacao`: etapa em que o caso foi criado (`pytest -m funcional`).
* `ce("CE-xx", ...)`: classes exercitadas.
* `defeito("DEF-xx", "descrição")`: defeito que o caso revela no código original. Com `SUT_VERSAO=original`, recebe `xfail(strict=True)`. No código corrigido, precisa passar.

## Integração com o V&V TestLab

Quando este repositório está dentro da pasta da ferramenta (`output/hotel-management-testado`), `iniciar-integracao.ps1` inicia a ponte local:

* `.\iniciar-integracao.ps1 -Versao original`: executa a suíte no código original; os defeitos aparecem como falhas e viram `DEF-xxx` no painel.
* `.\iniciar-integracao.ps1`: executa a suíte no código corrigido, com cobertura das funções do recorte e mutação pelo botão **Executar mutação** (`cosmic-ray.toml` + `scripts/selecionar_mutantes.py`, os mesmos 204 mutantes).
