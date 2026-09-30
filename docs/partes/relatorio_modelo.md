# Teste de software de terceiros: Hotel Management System

- **Aluno:** Gabriel Felipe Jess Meira
- **Disciplina:** Verificação e Validação
- **Sistema sob teste (SUT):** [CrystalWang1225/Hotel_Management_System](https://github.com/CrystalWang1225/Hotel_Management_System), commit `71b396bab15a840deab61a05d5c762173e8ea410`
- **Fork com testes e correções:** «FORK_URL» (tags `upstream-71b396b`, `sut-original`, `sut-corrigido`)
- **Ferramentas:** pytest 8.4.2, coverage.py via pytest-cov 6.3.0, Cosmic Ray 8.4.3, radon 6.0.1, pygount 3.1.0

## Sumário executivo

As três técnicas foram aplicadas na ordem exigida (**funcional → estrutural → baseada em defeitos**) sobre os três requisitos principais do sistema, todos ligados à reserva de quartos: **REQ-01 Reservar quartos** (incluindo a consulta de quartos livres que antecede a reserva), **REQ-02 Data de entrada** e **REQ-03 Data de saída**. Os demais requisitos funcionais foram catalogados (seção 1.2).

«RESUMO»

A cobertura e a mutação consideram as funções dos três requisitos em `hotel/views.py` (seção 5). Os testes revelaram **15 defeitos** nos três requisitos. O principal é um predicado de conflito de datas que é uma tautologia: depois da primeira reserva, o quarto nunca mais pode ser reservado, qualquer que seja a data de entrada ou de saída. Testes complementares do requisito secundário de cancelamento, feitos numa versão anterior do recorte, revelaram outros 4 defeitos (seção 9), totalizando **19**. Todos os defeitos foram corrigidos em commits separados no fork e confirmados pelos testes que os revelaram. A suíte final passa integralmente no programa corrigido. A mutação foi aplicada ao programa corrigido, que é o código submetido aos mutantes.

## 1. Seleção e caracterização do SUT

### 1.1 Origem, autoria e propósito

O *Hotel Management System* é uma aplicação web em Python de autoria de **Crystal Yuecen Wang**. Foi desenvolvida como projeto final da disciplina **ECE 464 – Databases**, sob orientação do professor Eugene Sokolov, e publicada no GitHub (8 commits, último em `71b396b`). Segundo o README, o objetivo é *"construir um sistema de gestão hoteleira eficiente e seguro, que ajude o negócio a se manter organizado e com as informações acessíveis"*. O público são hóspedes, que se cadastram, reservam, alteram, cancelam e pagam, e a administração do hotel, que mantém quartos e tipos de quarto no banco.

**Por que é adequado:** é software de terceiros, escrito em Python e com finalidade real de uso. Tem banco relacional (6 tabelas com chaves estrangeiras), autenticação por sessão, regras de negócio com datas, capacidade e custo, e várias rotas HTTP. Isso justifica aplicar as três técnicas. O tamanho (≈350 linhas de código, seção 2) permite chegar a análises completas, como cobertura de desvios de 100% e mutação sem amostragem, em vez de análises parciais.

**Arquitetura:** Flask 0.12 (rotas em `hotel/views.py`), WTForms/Flask-WTF (`hotel/forms.py`), SQLAlchemy/Flask-SQLAlchemy 2.1 (`hotel/models.py`), SQLite e templates Jinja2 com Bootstrap. As relações são `reservations.ruid → user.uid`, `booked.brid → reservations.rid`, `booked.room_id → rooms.room_number` e `payment.prid → reservations.rid`.

### 1.2 Requisitos funcionais do sistema e recorte

| RF | Funcionalidade | Rota | Situação no estudo |
|---|---|---|---|
| RF-01 | Cadastrar usuário | `/signup` | documentado |
| RF-02 | Entrar e sair (sessão) | `/signin`, `/logout` | pré-condição de REQ-01 (classes de sessão) |
| RF-03 | Listar quartos e tipos | `/rooms` | parte de REQ-01 (lista geral e resultado da consulta) |
| RF-04 | Consultar disponibilidade por período e hóspedes | `/available` → `/rooms` | parte de REQ-01; datas em REQ-02/REQ-03 |
| RF-05 | Reservar um ou mais quartos, com custo por diária | `/reserve` | **REQ-01**; datas em REQ-02/REQ-03 |
| RF-06 | Minha conta: dados, reservas, custos e pagamentos | `/about_user` | documentado (usado nas capturas) |
| RF-07 | Alterar reserva | `/update/<rid>` | documentado |
| RF-08 | Cancelar reserva | `/delete/<rid>` | documentado, com testes complementares |
| RF-09 | Registrar pagamento | `/payment/<rid>` | documentado |

**Recorte (3 requisitos principais), todos sobre a reserva de quartos:**

- **REQ-01 Reservar quartos:** um ou mais quartos (números inteiros, existentes, sem repetição) para 1 até a capacidade somada de hóspedes, somente se nenhum quarto tiver estadia com interseção no período. A reserva grava os vínculos e o custo e inclui a consulta de quartos livres que a antecede. Funções: `reserve`, `check_available`, `show_rooms`, `_ler_quartos`, `_quartos_ocupados`, `_periodos_conflitam`.
- **REQ-02 Data de entrada (check-in):** formato `MM/DD/AAAA`; não pode ser passada (hoje é permitido); pode coincidir com a **saída** de outra estadia do mesmo quarto. Vale na reserva e na consulta.
- **REQ-03 Data de saída (check-out):** formato `MM/DD/AAAA`; posterior à entrada (mínimo 1 noite); define o número de **diárias cobradas** (`cal_cost`); pode coincidir com a **entrada** de outra estadia do mesmo quarto. Vale na reserva e na consulta.

Os demais RFs não recebem testes completos. Alteração (RF-07) reaproveita as regras da reserva, e cadastro, conta e pagamento (RF-01, RF-06, RF-09) não têm regra de negócio verificável além da gravação. O cancelamento (RF-08) fazia parte de uma versão anterior do recorte; seus 8 casos continuam no repositório como testes complementares (`tests/test_04_secundarios.py`, marca `secundario`), fora das métricas.

### 1.3 Evidência de instalação e execução

O sistema foi instalado com `setup_local.ps1`. O script cria um ambiente Python 3.9 com versões compatíveis com o código de 2019. `compat.py` repõe `time.clock`, removido no Python 3.8 e usado por Flask-SQLAlchemy 2.1. `hotel/__init__.py` passou a ler a URI do banco de `HOTEL_DB_URI`. **Nenhuma regra de negócio foi alterada nessa preparação**: o diff entre `upstream-71b396b` e `sut-original` não toca `views.py`, `models.py` nem `forms.py`. As telas abaixo foram capturadas pelo script `scripts/capturar_telas.py`, que sobe o servidor com a base de demonstração e navega com o Microsoft Edge.

«TELAS»

## 2. Métricas de código

Medidas sobre o código do upstream (tag `upstream-71b396b`), extraído com `git archive`. Só entram `app.py` e o pacote `hotel/`. **Ficam de fora** os testes e scripts desta análise, os ambientes virtuais (`.venv*`) e as bibliotecas de front-end vendorizadas (`hotel/static/bootstrap`). Comando único: `python scripts/metricas_codigo.py`. As saídas completas estão em `evidencias/metricas/`.

| Métrica | Valor | Ferramenta e comando |
|---|---:|---|
| Módulos Python | 5 | `app.py`, `hotel/__init__.py`, `forms.py`, `models.py`, `views.py` |
| LOC (linhas físicas) | 428 | `radon raw -s app.py hotel` |
| SLOC (linhas de código) | 354 | `radon raw -s app.py hotel` |
| LLOC (linhas lógicas) | 341 | `radon raw -s app.py hotel` |
| Linhas de código (pygount) | 352 | `pygount --format=summary --suffix=py app.py hotel` |
| Classes | 12 | `radon cc -s -a app.py hotel` (6 formulários + 6 modelos) |
| Funções | 13 | idem (12 em `views.py` + `length_check`) |
| Métodos | 6 | idem (construtores dos modelos) |
| Complexidade ciclomática média / máxima | 5,0 / 25 | idem; `reserve` = 25 e `update_reservation` = 24 (grau D) |

A diferença entre SLOC do radon (354) e *Code* do pygount (352) vem das duas linhas de docstring/continuação que cada ferramenta classifica de forma distinta. `reserve` (CC = 25) e `show_rooms` (CC = 16), as funções mais complexas do sistema, estão no recorte.

## 3. Metodologia

**Oráculos.** Os resultados esperados vêm do README ("check-in no passado", "quartos indisponíveis no período", "quartos que não comportam o número de hóspedes", "a reserva só pode ser alterada/excluída pelo usuário em *My Account*") e da interface, que traz os formulários com datas `MM/DD/AAAA`, hóspedes inteiros e quartos separados por vírgula. Para o que o README não fixa, foram adotadas convenções declaradas: estadia como intervalo semiaberto `[entrada, saída)`, em que um hóspede pode entrar no dia em que outro sai; métodos HTTP seguros, em que `GET` não altera dados; e integridade referencial ao cancelar.

**Ambiente.** Windows 11, Python 3.9.25 (aplicação e pytest) e Python 3.12 (Cosmic Ray, em ambiente separado porque exige SQLAlchemy ≥ 1.4, incompatível com Flask-SQLAlchemy 2.1). Cada caso usa SQLite em memória recriado pela fixture `baseline`, com três quartos (101: R$ 100/noite, 2 pessoas; 102: R$ 150, 3; 103: R$ 200, 4) e dois usuários (Ana e Bruno). As datas são relativas ao dia da execução, para manter a suíte reproduzível.

**Versões do SUT.** A variável `SUT_VERSAO` escolhe o código importado pelos testes. Com `original`, é usado `.sut-original/hotel`, extraído da tag `sut-original`. Com `corrigida`, é usado `hotel/`. Na versão original, cada caso marcado `@pytest.mark.defeito("DEF-xx", ...)` recebe `xfail(strict=True)`: ele **precisa falhar** para confirmar que o defeito existe. Se um defeito "sumir", o `XPASS` estrito quebra a execução. Na versão corrigida, nenhum caso é marcado e todos precisam passar.

**Rastreabilidade.** Cada função de teste leva o identificador do caso no nome (`test_CT_001_...`), a etapa em que foi criado (`@pytest.mark.funcional`, `estrutural` ou `mutacao`), as classes que exercita (`@pytest.mark.ce("CE-01", ...)`) e, quando é o caso, o defeito revelado. O plugin em `tests/conftest.py` exporta essa matriz (`--rastreabilidade`), e `scripts/evolucao.py` verifica que **toda classe de equivalência tem ao menos um caso funcional** (Apêndice A). A cadeia é REQ → CE → CT → execução pytest → DEF → commit de correção.

**Execução.** `etapas.ps1` roda tudo em sequência e grava as evidências em `evidencias/<etapa>/`: `pytest.txt` (saída `-v -rxX` e relatório `term-missing`), `junit.xml`, `coverage.json`, `htmlcov/`, `rastreabilidade.json` e `cobertura-recorte.json`. A ordem das etapas também aparece no histórico do fork (seção 6).

**Gestão dos testes (V&V TestLab).** Requisitos, classes, casos, execuções, defeitos e métricas também foram organizados no V&V TestLab, uma aplicação web local de gestão de testes. Ela se conecta ao repositório por uma ponte HTTP restrita a `127.0.0.1` (`integration/vv_bridge.py`), que executa o pytest com coverage.py e o Cosmic Ray e importa o JUnit, a cobertura das funções do recorte e o escore de mutação, vinculando cada resultado ao caso pelo identificador `CT-xxx`. O projeto importável (`output/hotel-vvtestlab-projeto-inicial.json`) e o estudo completo (`output/hotel-vvtestlab-backup.json`) são gerados das mesmas evidências deste relatório.

![Matriz de rastreabilidade do V&V TestLab com o estudo do hotel carregado.](../evidencias/telas-vvtestlab/04-rastreabilidade.png)

*Matriz de rastreabilidade do V&V TestLab com o estudo do hotel carregado.*

## 4. Etapa 1: teste funcional

### 4.1 Classes de equivalência

As condições de entrada dos três requisitos foram particionadas em **42 classes** (23 válidas e 19 inválidas): 27 em REQ-01, 6 em REQ-02 e 9 em REQ-03. A tabela é gerada do catálogo `tests/classes_equivalencia.json`, o mesmo que o script de rastreabilidade usa para verificar a cobertura das classes. Os identificadores CE não são sequenciais porque foram preservados entre revisões do recorte: CE-43 a CE-48 vieram da revisão dos formatos (commit `8bf46d8`) e CE-49 a CE-55 da separação entre data de entrada e data de saída.

«TABELA_CE»

**Regra de derivação.** Um caso pode cobrir várias classes válidas ao mesmo tempo (CT-001 cobre onze). Cada classe inválida tem ao menos um caso próprio, em que **todas as outras entradas são válidas**, para que a rejeição só possa ser atribuída àquela classe. Por isso o CT-016 usa `101,999` com 2 hóspedes, e não `999` com 0 hóspedes, o que misturaria CE-14 e CE-09.

### 4.2 Análise do valor limite

Datas relativas a hoje (D). Reserva existente usada nos limites de interseção: quarto 101 de D+10 a D+12.

| Req. | Variável (limite) | Imediatamente abaixo | No limite | Imediatamente acima | Justificativa |
|---|---|---|---|---|---|
| REQ-01 | Hóspedes, mínimo (1) | 0 → rejeitar (CT-007) | 1 → aceitar (CT-006) | 2 → aceitar (CT-003) | Uma reserva precisa de ao menos um hóspede. |
| REQ-01 | Hóspedes, máximo de 1 quarto (101: 2) | 1 → aceitar (CT-006) | 2 → aceitar (CT-003) | 3 → rejeitar (CT-004) | A capacidade é o limite superior de CE-08. |
| REQ-01 | Hóspedes, máximo somado (101+102: 5) | 4 → aceitar (CT-060) | 5 → aceitar (CT-002) | 6 → rejeitar (CT-005) | Verifica se a capacidade é somada quando há vários quartos. |
| REQ-01 | Hóspedes na consulta (mín. 1) | 0 → recusar (CT-039) | 1 → aceitar (CT-042) | 2 → aceitar (CT-040) | Mesma regra da reserva, no filtro. |
| REQ-01 | Capacidade do 101 (2) na consulta | 1 → exibe 101 (CT-042) | 2 → exibe 101 (CT-040) | 3 → omite 101 (CT-041) | Fronteira de CE-41/CE-42. |
| REQ-02 | Data de entrada (mín. = hoje) | D−1 → rejeitar (CT-013) | D → aceitar (CT-011) | D+1 → aceitar (CT-012) | O README exige "pelo menos hoje"; a fronteira passado/presente é onde se costuma errar comparando data com data-hora. |
| REQ-02 | Entrada × saída existente (D+12), na reserva | entrada D+11 → conflito (CT-020) | entrada D+12 → livre (CT-022) | entrada D+13 → livre (CT-062) | Com intervalo `[entrada, saída)`, entrar no dia em que o outro sai não conflita. |
| REQ-02 | Entrada × saída existente (D+12), na consulta | entrada D+11 → omite 101 (CT-036) | entrada D+12 → exibe (CT-034) | entrada D+13 → exibe (CT-064) | Mesmo limite, agora no filtro da consulta. |
| REQ-03 | Duração da reserva (mín. = 1 noite) | 0 → rejeitar (CT-009) | 1 → aceitar, custo 100 (CT-008) | 2 → aceitar, custo 200 (CT-001) | Saída = entrada não gera diária; −1 (CT-010) representa CE-07; 4 noites custam 4 diárias (CT-067). |
| REQ-03 | Período da consulta (mín. = 1 noite) | 0 → recusar (CT-038) | 1 → aceitar (CT-043) | 2 → aceitar (CT-032) | Mesma regra da reserva; −2 (CT-037) representa saída antes da entrada. |
| REQ-03 | Saída × entrada existente (D+10), na reserva | saída D+11 → conflito (CT-019) | saída D+10 → livre (CT-021) | saída D+9 → livre (CT-061) | Sair no dia em que o outro entra não conflita. |
| REQ-03 | Saída × entrada existente (D+10), na consulta | — | saída D+10 → exibe (CT-035) | saída D+9 → exibe (CT-063) | Mesmo limite no filtro; o lado "abaixo" é o mesmo cenário de CT-036. |

### 4.3 Casos funcionais e resultados no código original

«CASOS_FUNCIONAIS»

**Resultado (código original, `evidencias/funcional-original/`):** 50 casos, **22 passaram e 28 falharam** confirmando 12 defeitos dos três requisitos (DEF-01 a DEF-07, DEF-12 a DEF-14, DEF-18 e DEF-19). As falhas têm causas distintas, conferidas com `--runxfail`: `KeyError: 'user_available'`, `ValueError` em `int('abc')`, `TypeError` em `combine(None)`, além de redirecionamentos e listagens diferentes do oráculo. Por requisito (pelo requisito da classe principal de cada caso): REQ-01 com 34 casos, REQ-02 com 7 e REQ-03 com 9. Cobertura do recorte: **84/92 comandos (91,3%) e 42/50 desvios (84,0%)**.

## 5. Etapa 2: teste estrutural

### 5.1 Meta de cobertura e justificativa

**Critério:** todos-os-nós e todos-os-arcos (comandos e desvios, `coverage run --branch`) nas quatro funções que implementam os três requisitos: `reserve` (reserva e validação das datas), `cal_cost` (diárias entre entrada e saída), `check_available` (validação das datas e hóspedes da consulta) e `show_rooms` (quartos livres no período), com «ORIG_CMD» comandos e «ORIG_DESV» desvios no original. **Meta: 100% dos comandos e 100% dos desvios viáveis.**

Justificativa:

1. O recorte é pequeno e concentra toda a regra de negócio testada, então a meta máxima tem custo baixo.
2. Cobertura de desvios subsume a de comandos e obriga a exercitar os ramos falsos (sessão encerrada, laço sem conflito), justamente onde a etapa funcional deixou lacunas.
3. Critérios mais fortes, como caminhos simples, explodem combinatoriamente por causa dos laços aninhados de `reserve`/`show_rooms` (três níveis) e trariam pouco ganho diante do teste de mutação da etapa seguinte.

A medição é restrita ao recorte porque medir `views.py` inteiro misturaria rotas deliberadamente não testadas (cadastro, login, alteração, pagamento) e tornaria qualquer meta global arbitrária.

### 5.2 Lacunas após a etapa funcional e casos acrescentados

| Trecho não coberto (original) | Por que ficou de fora | Caso estrutural |
|---|---|---|
| `show_rooms` 166–167, `check_available` 180–181, `reserve` 242–243 (ramo falso de `if session['user_available']`) | Os casos funcionais sem sessão não criam a chave, e o original lança `KeyError` antes do `if`; o ramo falso só roda com a chave valendo `False`, estado deixado pelo `logout` | CT-048 |
| `check_available` 179 (desvio 175→179) | A etapa funcional só fazia `POST` | CT-049 |
| `reserve` 241 (desvio 189→241) | Idem | CT-050 |
| `reserve` desvios 208→205 e 205→204 (vínculo de outro quarto; fim do laço interno sem conflito) | Nos casos funcionais, todas as reservas prévias eram do mesmo quarto | CT-044 |
| `reserve` desvio 230→229 (`if each.rid > current_id` falso) | **Inviável:** os IDs vêm em ordem crescente de chave primária, então cada `rid` supera o máximo anterior | — |

A leitura do código para essas lacunas expôs mais três defeitos, que ganharam casos próprios: CT-045 (DEF-15, laço triplo sem `brid == rid`), CT-046 (DEF-16, variável global `global_avail`) e CT-047 (DEF-17, `remove` durante a iteração).

| Caso | Classes | Cenário | Esperado | Original |
|---|---|---|---|---|
| CT-044 | CE-17, CE-19 | Bruno tem o 102 em D+10; Ana reserva o 101 em D+10 | aceita | passou |
| CT-045 | CE-17 | Ana tem o 101 em D+10, Bruno tem o 102 em D+20; reservar o 101 em D+20 | aceita | **falhou – DEF-15** (mascarado por DEF-01) |
| CT-046 | CE-33 | Ana consulta D+10 com o 101 ocupado; Bruno, em outra sessão, abre `/rooms` sem filtro | Bruno vê 101, 102, 103 | **falhou – DEF-16** (vê 102, 103) |
| CT-047 | CE-40 | 101 e 102 ocupados em D+10; consulta D+10, 1 hóspede | só o 103 | **falhou – DEF-17** (102 aparece) |
| CT-048 | CE-02, CE-32 | `user_available = False` em `/reserve`, `/available` e `/rooms` (e `POST /delete`) | redireciona e preserva | passou |
| CT-049 | CE-31 | `GET /available` autenticado | formulário com `checkin_date` | passou |
| CT-050 | CE-01 | `GET /reserve` autenticado | formulário com `room_numbers` | passou |

**Resultado (código original, `evidencias/estrutural-original/`):** 57 casos, 26 passaram e 31 falharam (xfail estrito). Cobertura do recorte: **92/92 comandos (100%) e 49/50 desvios (98,0%)**. A meta foi atingida, porque o desvio restante é inviável.

## 6. Correção dos defeitos antes da mutação

A mutação precisa de uma suíte que passe no programa mutado. Por isso os defeitos foram corrigidos **antes** de gerar os mutantes, em commits separados no fork, cada um citando a causa e os casos que o confirmam. O diff completo está em `evidencias/correcoes.diff` (`git diff sut-original sut-corrigido -- hotel`).

| Commit | Defeitos | Casos que passaram a passar |
|---|---|---|
| `8a6c4bd` | DEF-07 (sessão sem chave → `KeyError`) | CT-014, CT-031 (e CT-025, complementar) |
| `2d1b2cd` | DEF-01 (tautologia), DEF-15 (produto cartesiano) | CT-021, 022, 023, 033, 034, 035, 061–064, 045 |
| `704bc86` | DEF-02 (entrada hoje) | CT-011 |
| `644fd0d` | DEF-03, 04, 05, 06, 18, 19 (validação da reserva; transação única) | CT-007, 015, 016, 017, 051, 052, 065, 068 |
| `1313f12` | DEF-08, 09, 10, 11 (RF-08 cancelamento, secundário; template com `POST`) | CT-026, 027, 028, 029 (complementares) |
| `9e66e2d` | DEF-12, 13, 14, 16, 17, 18 (consulta; filtro na sessão) | CT-037, 038, 039, 041, 053, 054, 066, 046, 047 |

Em cada passo, a suíte inteira foi executada para confirmar que nenhum caso que já passava regrediu. **Resultado final no programa corrigido (tag `sut-corrigido`, `evidencias/suite-corrigida/`): 57/57 casos passaram**, sem `skip` nem `xfail`, com cobertura do recorte de **92/92 comandos e 38/38 desvios (100%)**. Os 8 complementares também passam. O código corrigido tem menos desvios que o original (38 contra 50) porque os laços triplos foram trocados por uma junção SQL e por compreensões de conjunto. As funções auxiliares (`_sessao_autenticada`, `_periodos_conflitam`, `_quartos_ocupados`, `_ler_quartos`) entram no recorte medido.

Um ajuste de oráculo foi necessário e está registrado no commit `8a6c4bd`. O CT-025 esperava que o cancelamento sem sessão redirecionasse para `/`, mas o sistema redireciona para `/rooms`, que exige login e então leva a `/`. Isso não é defeito do software: o requisito verificado, preservar a reserva, não mudou.

## 7. Etapa 3: teste baseado em defeitos (mutação)

### 7.1 Configuração e escopo

* **Ferramenta:** Cosmic Ray 8.4.3, distribuidor local, timeout de 30 s por mutante e todos os operadores padrão: substituição de operadores relacionais, aritméticos, lógicos e unários, troca de números, de `break`/`continue` e de palavras-chave, laço de zero iterações, remoção de decorador etc.
* **Escopo:** **todos os mutantes** gerados nas linhas das funções dos três requisitos no `hotel/views.py` corrigido, sem amostragem: `reserve`, `cal_cost`, `check_available`, `show_rooms` e as quatro auxiliares. Total: **«MUT_TOTAL» mutantes**. As demais rotas, inclusive `delete_reservation` (RF-08, secundário), foram excluídas porque não fazem parte do recorte; incluí-las só acrescentaria sobreviventes triviais.
* **Configuração:** `mutacao/cosmic-ray-inicial.toml` e `mutacao/cosmic-ray-final.toml`. O comando de teste é `pytest -x -q`, restrito a `-m 'funcional or estrutural'` na rodada inicial e a `-m 'funcional or estrutural or mutacao'` na final (os complementares ficam de fora). O script `scripts/mutacao.py` monta a sessão, executa `cosmic-ray exec` e grava `sessao.sqlite`, `resumo.json`, `sobreviventes.txt` (diff de cada sobrevivente) e `execucao.txt`.
* **Escore:** mortos / (mortos + sobreviventes). Não houve mutantes incompetentes nem *timeouts*.

### 7.2 Rodada inicial (suíte ao fim da etapa estrutural)

**189 mutantes: 178 mortos e 11 sobreviventes. Escore de 94,2%.** Execução em cerca de 6 minutos.

| # | Função (linha) | Mutação | Classificação | Ação |
|---|---|---|---|---|
| S1 | `_quartos_ocupados` (23) | `Booked.brid == Reservations.rid` → `>=` | **Não equivalente.** Nenhum caso tinha um vínculo de reserva *posterior* capaz de herdar as datas de uma reserva *anterior* de outro quarto | **CT-055** |
| S2 | `_ler_quartos` (34) | `set(numeros) <= existentes` → `<` | **Não equivalente.** Nenhum caso reservava *todos* os quartos do hotel | **CT-056** |
| S3 | `cal_cost` (268) | `each_room_id == e.room_number` → `is` | **Não equivalente.** `is` só coincide com `==` para inteiros de −5 a 256, que o CPython mantém em cache; os quartos da base eram 101–103 | **CT-059** (quarto 301) |
| S4 | `check_available` (197) | `request.method == 'POST'` → `>=` | **Equivalente.** A rota só admite `GET`, `POST`, `HEAD` e `OPTIONS`, e nenhum método diferente de `POST` é ≥ `'POST'` na ordem lexicográfica | — |
| S5 | `reserve` (217) | idem | **Equivalente** (mesmo raciocínio) | — |
| S6 | `reserve` (226) | `time(0, 0)` → `time(1, 0)` em `d1` | **Equivalente.** `d1` só é comparado com datas à meia-noite (`d2` e datas gravadas) e com `date.today()` via `d1.date()`; deslocar a hora de `d1` dentro do mesmo dia não inverte nenhuma comparação, e o valor gravado é `checkin`, não `d1` | — |
| S7 | `reserve` (226) | `time(0, 0)` → `time(0, 1)` | **Equivalente** (idem) | — |
| S8 | `reserve` (247) | custo inicial `0` → `1` | **Equivalente.** O valor é sobrescrito por `cal_cost` antes do único `commit` | — |
| S9 | `reserve` (247) | custo inicial `0` → `-1` | **Equivalente** (idem) | — |
| S10 | `_ler_quartos` (34) | `len(set(n)) != len(n)` → `<` | **Equivalente.** Um conjunto nunca tem mais elementos que a lista de origem, então `!=` e `<` são a mesma condição | — |
| S11 | `_ler_quartos` (34) | `len(set(n)) != len(n)` → `is not` | **Equivalente no domínio.** Os comprimentos só passam de 256 se o usuário informar mais de 256 quartos numa reserva, o que é irrealista; abaixo disso, o cache de inteiros do CPython torna `is not` idêntico a `!=` | — |

### 7.3 Casos acrescentados e rodada final

| Caso | Classes | Cenário | Esperado | Mata |
|---|---|---|---|---|
| CT-055 | CE-17 | Ana tem o 102 em D+10 (reserva 1); Bruno tem o 101 em D+20 (reserva 2); Ana reserva o 101 em D+10 | aceita | S1 |
| CT-056 | CE-13, CE-20 | Reservar 101, 102 e 103 para 9 hóspedes por 2 noites | aceita; custo 900; 3 vínculos | S2 |
| CT-059 | CE-05, CE-19 | Quarto 301 (R$ 120) por 2 noites | custo 240 | S3 |

**Rodada final (suíte completa, 60 casos, `evidencias/mutacao-final/`): «MUT_FINAL_TEXTO»

### 7.4 Fragilidades reveladas

A suíte tinha 100% de cobertura de desvios e, mesmo assim, deixou vivos 3 mutantes não equivalentes. As fragilidades expostas foram:

1. **Dados de teste homogêneos.** Todos os números de quarto cabiam no cache de inteiros pequenos do Python, o que esconde a troca de `==` por `is` no cálculo das diárias. Em produção, com quartos numerados como 301, esse erro passaria despercebido.
2. **Cenários de ocupação sempre com a mesma ordem de criação.** Faltava o caso em que a reserva mais nova pertence ao quarto pedido e a mais antiga a outro quarto, justamente o que distingue a junção correta (`brid == rid`) de uma errada.
3. **Nenhum caso no extremo superior da enumeração de quartos**, isto é, reservar todos eles.

Nos testes complementares do cancelamento, a mesma análise (feita quando o cancelamento estava no recorte) gerou CT-057 e CT-058, que mostraram a mesma fragilidade de dados homogêneos (uid 1000) e um oráculo de autorização testado num só sentido.

Os 8 equivalentes vêm de código defensivo ou redundante que veio do original: o custo provisório 0 e `time(0, 0)` explícito. Eles mostram também que o escore bruto subestima a qualidade da suíte. Excluindo os equivalentes, o escore final é «MUT_AJUSTADO».

## 8. Evolução incremental

«EVOLUCAO»

A ordem **Funcional → Estrutural → (correção) → Mutação** está no histórico do fork (os commits posteriores reorganizaram o recorte e completaram casos, sempre reexecutando todas as etapas): `afeb312` (etapa 1), `ac975b7` (etapa 2), seis commits de correção, e `324e29a` (etapa 3). Cada etapa só acrescenta casos. Nenhum caso das etapas anteriores foi removido ou marcado com `skip`.

## 9. Registro de defeitos

Linhas referentes ao `hotel/views.py` original (`sut-original`). Todos os defeitos têm teste automatizado que falha no original e passa no corrigido. **DEF-08 a DEF-11 pertencem ao RF-08 (cancelamento, secundário)** e foram revelados pelos testes complementares; os outros 15 pertencem aos três requisitos principais.

«DEFEITOS»

**Fora do recorte:** `update_reservation`, `about_user` e `payment` repetem a causa de DEF-07 (`session['user_available']`), e `update_reservation` repete a de DEF-01 e DEF-15. Eles não foram corrigidos nem testados por estarem fora do escopo. A correção seria a mesma, reutilizando `_sessao_autenticada` e `_quartos_ocupados`.

### 9.1 Testes complementares do requisito secundário RF-08 (cancelar reserva)

Numa versão anterior do recorte, o cancelamento era um dos três requisitos principais. Seus casos continuam executáveis em `tests/test_04_secundarios.py` (marca `secundario`), com as classes CE-21 a CE-30, mas ficam fora das métricas de cobertura e de mutação. Evidências: `evidencias/secundarios-original/` e `evidencias/secundarios-corrigida/`.

«CASOS_SECUNDARIOS»

## 10. Interpretação da cobertura e limitações

* **Cobertura não é ausência de defeitos.** Na etapa 2, o código original tinha 100% de comandos cobertos e 31 casos falhando. Em `show_rooms`, por exemplo, a linha do predicado tautológico era executada em todos os casos da consulta e sempre errava. Cobertura mede o que foi *executado*, não o que foi *verificado*. Quem revela o defeito é o oráculo.
* **Comandos × desvios.** Depois da etapa 1, a cobertura de comandos (91,3%) era 7 pontos maior que a de desvios (84,0%). Os desvios 205→204 e 208→205 estavam em linhas executadas, mas um dos lados da decisão nunca ocorreu. Esse lado era o caso "vínculo de outro quarto", que depois levou ao DEF-15.
* **Desvio inviável.** O 230→229 do original não pode ser coberto porque as consultas retornam as reservas em ordem de chave primária. A correção eliminou esse laço.
* **Global × recorte.** No `views.py` inteiro, a cobertura final é de «COV_VIEWS_TOTAL». O restante corresponde a rotas fora do escopo. É uma lacuna declarada, não um defeito da suíte.
* **100% de desvios ≠ suíte forte.** A etapa 3 mostrou 3 mutantes não equivalentes vivos com 100% de desvios.
* **Limitações.**
    * Os testes usam o cliente de teste do Flask e SQLite em memória: não há automação de navegador, carga ou concorrência real (duas reservas simultâneas do mesmo quarto não foram testadas).
    * A proteção CSRF não é validada pelas rotas do original; a correção de DEF-10 (`POST`) reduz o risco, mas não o elimina.
    * As senhas são gravadas em texto plano (`models.py`), fora do recorte.
    * Alguns oráculos são convenções declaradas (seção 3), não requisitos escritos pela autora.
    * O Cosmic Ray foi aplicado só às funções dos três requisitos; RF-07 (alteração) repete as regras de datas e não foi testado.

## 11. Conclusões e lições aprendidas

1. **A técnica funcional encontrou a maior parte dos defeitos** (12 dos 15 dos três requisitos) sem olhar o código, porque as classes inválidas e os limites foram tratados um a um. O limite "entrada hoje" e as estadias adjacentes expuseram defeitos que valores típicos não mostrariam.
2. **A técnica estrutural encontrou o que a especificação não sugere:** estado global compartilhado, remoção durante a iteração e produto cartesiano. Ela também mostrou que um defeito (DEF-15) pode ficar **mascarado** por outro (DEF-01), só aparecendo depois da primeira correção.
3. **A mutação avaliou os próprios testes.** Com 100% de desvios, a suíte ainda tinha fragilidades concretas (dados homogêneos, ordem de criação fixa), corrigidas com 3 casos pequenos.
4. **Corrigir antes de mutar é indispensável.** Mutar o original, com 31 testes falhando, invalidaria o escore, porque um mutante que "corrige" um defeito seria contado como vivo ou morto por acaso.
5. **Dificuldades:**
    * dependências de 2019 incompatíveis com o Python atual, resolvidas com ambientes separados e `compat.py`;
    * a execução do Cosmic Ray no Windows (caminho relativo do interpretador);
    * a decisão sobre oráculos não escritos, resolvida declarando convenções.

## 12. Reprodução

```powershell
git clone «FORK_URL» ; cd Hotel_Management_System
./setup_local.ps1          # ambientes .venv (Python 3.9) e .venv-mutation (Python 3.12) via uv
./etapas.ps1               # métricas, etapas 1-2 (original), suíte corrigida, mutação inicial/final, suíte final
./executar.ps1             # sistema em http://127.0.0.1:5000 (ana@example.test / senha123)
```

Comandos isolados:

* `SUT_VERSAO=original pytest -m funcional -rxX`
* `pytest --cov=hotel.views --cov-branch --cov-report=term-missing`
* `.venv-mutation/Scripts/python.exe scripts/mutacao.py final`
* `git diff sut-original sut-corrigido -- hotel`

## Apêndice A: rastreabilidade classe → casos

«RASTREABILIDADE»
