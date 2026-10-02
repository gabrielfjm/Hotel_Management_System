# Teste de software de terceiros: Hotel Management System

- **Aluno:** Gabriel Felipe Jess Meira
- **Disciplina:** Verificação e Validação
- **Sistema sob teste (SUT):** [CrystalWang1225/Hotel_Management_System](https://github.com/CrystalWang1225/Hotel_Management_System), commit `71b396bab15a840deab61a05d5c762173e8ea410`
- **Fork com testes e correções:** «FORK_URL» (tags `upstream-71b396b`, `sut-original`, `sut-corrigido`)
- **Ferramentas:** pytest 8.4.2, coverage.py via pytest-cov 6.3.0, Cosmic Ray 8.4.3, radon 6.0.1, pygount 3.1.0

## Sumário executivo

As três técnicas foram aplicadas na ordem exigida (**funcional → estrutural → baseada em defeitos**) sobre os três requisitos principais do sistema, todos ligados à reserva de quartos: **REQ-01 Reservar quartos**, **REQ-02 Data de entrada** e **REQ-03 Data de saída**. Os demais requisitos funcionais foram catalogados (seção 1.2). Os **mesmos 15 casos de teste** foram usados nas três etapas: a etapa estrutural reaproveitou 5 deles para percorrer os grafos de fluxo e ampliou 3 com o cenário que faltava para a cobertura; a de mutação rodou os 15 contra cada mutante e ampliou 4 para matar os sobreviventes. Nenhum caso novo foi criado depois da etapa funcional.

«RESUMO»

A cobertura e a mutação consideram as funções dos três requisitos em `hotel/views.py` (seção 5). Os testes revelaram **10 defeitos** nos três requisitos. O principal é um predicado de conflito de datas que é uma tautologia: depois da primeira reserva, o quarto nunca mais pode ser reservado, qualquer que seja a data de entrada ou de saída. Testes complementares de dois requisitos secundários, cancelamento (RF-08) e consulta de disponibilidade (RF-04), revelaram outros 9 defeitos (seção 9), totalizando **19**. Todos os defeitos foram corrigidos em commits separados no fork e confirmados pelos testes que os revelaram. A suíte final passa integralmente no programa corrigido. A mutação foi aplicada ao programa corrigido, que é o código submetido aos mutantes.

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
| RF-03 | Listar quartos e tipos | `/rooms` | documentado (destino da reserva e da consulta) |
| RF-04 | Consultar disponibilidade por período e hóspedes | `/available` → `/rooms` | documentado, com testes complementares |
| RF-05 | Reservar um ou mais quartos, com custo por diária | `/reserve` | **REQ-01**; datas em REQ-02/REQ-03 |
| RF-06 | Minha conta: dados, reservas, custos e pagamentos | `/about_user` | documentado (usado nas capturas) |
| RF-07 | Alterar reserva | `/update/<rid>` | documentado |
| RF-08 | Cancelar reserva | `/delete/<rid>` | documentado, com testes complementares |
| RF-09 | Registrar pagamento | `/payment/<rid>` | documentado |

**Recorte (3 requisitos principais), todos sobre a reserva de quartos:**

- **REQ-01 Reservar quartos:** um ou mais quartos (números inteiros, existentes, sem repetição) para 1 até a capacidade somada de hóspedes, somente se nenhum quarto tiver estadia com interseção no período. A reserva grava os vínculos e o custo. Funções: `reserve`, `_ler_quartos`, `_quartos_ocupados`, `_periodos_conflitam`.
- **REQ-02 Data de entrada (check-in):** formato `MM/DD/AAAA`; não pode ser passada (hoje é permitido); pode coincidir com a **saída** de outra estadia do mesmo quarto.
- **REQ-03 Data de saída (check-out):** formato `MM/DD/AAAA`; posterior à entrada (mínimo 1 noite); define o número de **diárias cobradas** (`cal_cost`); pode coincidir com a **entrada** de outra estadia do mesmo quarto.

Os demais RFs não recebem testes completos. Alteração (RF-07) reaproveita as regras da reserva, e cadastro, conta e pagamento (RF-01, RF-06, RF-09) não têm regra de negócio verificável além da gravação. A consulta de disponibilidade (RF-04) antecede a reserva, mas tem formulário e regras próprias; para manter o recorte enxuto, ela e o cancelamento (RF-08) ficaram como requisitos secundários, com 14 casos complementares (`tests/test_04_secundarios.py`, marca `secundario`) fora das métricas.

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

A diferença entre SLOC do radon (354) e *Code* do pygount (352) vem das duas linhas de docstring/continuação que cada ferramenta classifica de forma distinta. `reserve` (CC = 25), a função mais complexa do sistema, está no recorte.

## 3. Metodologia

**Oráculos.** Os resultados esperados vêm do README ("check-in no passado", "quartos indisponíveis no período", "quartos que não comportam o número de hóspedes", "a reserva só pode ser alterada/excluída pelo usuário em *My Account*") e da interface, que traz os formulários com datas `MM/DD/AAAA`, hóspedes inteiros e quartos separados por vírgula. Para o que o README não fixa, foram adotadas convenções declaradas: estadia como intervalo semiaberto `[entrada, saída)`, em que um hóspede pode entrar no dia em que outro sai; métodos HTTP seguros, em que `GET` não altera dados; e integridade referencial ao cancelar.

**Ambiente.** Windows 11, Python 3.9.25 (aplicação e pytest) e Python 3.12 (Cosmic Ray, em ambiente separado porque exige SQLAlchemy ≥ 1.4, incompatível com Flask-SQLAlchemy 2.1). Cada caso usa SQLite em memória recriado pela fixture `baseline`, com três quartos (101: R$ 100/noite, 2 pessoas; 102: R$ 150, 3; 301: R$ 200, 4) e dois usuários (Ana e Bruno). As datas dos casos são reais e fixas (março de 2030, no futuro, para a suíte continuar válida); só os casos de "hoje" e "ontem" usam a data do dia da execução.

**Versões do SUT.** A variável `SUT_VERSAO` escolhe o código importado pelos testes. Com `original`, é usado `.sut-original/hotel`, extraído da tag `sut-original`. Com `corrigida`, é usado `hotel/`. Na versão original, cada caso marcado `@pytest.mark.defeito("DEF-xx", ...)` recebe `xfail(strict=True)`: ele **precisa falhar** para confirmar que o defeito existe. Se um defeito "sumir", o `XPASS` estrito quebra a execução. Na versão corrigida, nenhum caso é marcado e todos precisam passar.

**Rastreabilidade.** Cada função de teste leva o identificador do caso no nome (`test_CT_001_...`). A parte funcional de cada caso tem a marca `@pytest.mark.funcional`; as ampliações feitas nas etapas seguintes são outras funções com o **mesmo identificador** e a marca da etapa (`estrutural` ou `mutacao`), como `test_CT_001_ampliacao_...`. Cada função traz ainda as classes que exercita (`@pytest.mark.ce("CE-01", ...)`) e, quando é o caso, o defeito revelado. O plugin em `tests/conftest.py` exporta essa matriz (`--rastreabilidade`), e `scripts/evolucao.py` verifica que **toda classe de equivalência tem ao menos um caso funcional** (Apêndice A). A cadeia é REQ → CE → CT → execução pytest → DEF → commit de correção.

**Execução.** `etapas.ps1` roda tudo em sequência e grava as evidências em `evidencias/<etapa>/`: `pytest.txt` (saída `-v -rxX` e relatório `term-missing`), `junit.xml`, `coverage.json`, `htmlcov/`, `rastreabilidade.json` e `cobertura-recorte.json`. A ordem das etapas também aparece no histórico do fork (seção 6).

**Gestão dos testes (V&V TestLab).** Requisitos, classes, casos, execuções, defeitos e métricas também foram organizados no V&V TestLab, uma aplicação web local de gestão de testes. Ela se conecta ao repositório por uma ponte HTTP restrita a `127.0.0.1` (`integration/vv_bridge.py`), que executa o pytest com coverage.py e o Cosmic Ray e importa o JUnit, a cobertura das funções do recorte e o escore de mutação, vinculando cada resultado ao caso pelo identificador `CT-xxx`. O projeto importável (`output/hotel-vvtestlab-projeto-inicial.json`) e o estudo completo (`output/hotel-vvtestlab-backup.json`) são gerados das mesmas evidências deste relatório.

![Matriz de rastreabilidade do V&V TestLab com o estudo do hotel carregado.](../evidencias/telas-vvtestlab/04-rastreabilidade.png)

*Matriz de rastreabilidade do V&V TestLab com o estudo do hotel carregado.*

## 4. Etapa 1: teste funcional

### 4.1 Classes de equivalência

As condições de entrada dos três requisitos foram particionadas em **22 classes** (11 válidas e 11 inválidas): 16 em REQ-01, 4 em REQ-02 e 2 em REQ-03. A tabela é gerada do catálogo `tests/classes_equivalencia.json`, o mesmo que o script de rastreabilidade usa para verificar a cobertura das classes. As classes dos requisitos secundários (CE-31 a CE-47) estão no mesmo catálogo e são usadas só pelos casos complementares.

«TABELA_CE»

**Regra de derivação.** Um caso pode cobrir várias classes válidas ao mesmo tempo (CT-001 cobre dez). Cada classe inválida tem exatamente um caso próprio, em que **todas as outras entradas são válidas**, para que a rejeição só possa ser atribuída àquela classe. Por isso o CT-007 usa `101,999` com 2 hóspedes, e não `999` com 0 hóspedes, o que misturaria CE-06 e CE-12. Assim, 11 casos cobrem as 11 classes inválidas e 4 casos cobrem as válidas e os limites.

### 4.2 Análise do valor limite

Hoje = dia da execução (D). Reserva existente usada nos limites de interseção: quarto 101 de 10/03/2030 a 12/03/2030. Para manter a suíte enxuta, os pontos de limite foram embutidos nos próprios casos de classe: o caso de cada classe inválida usa o valor imediatamente fora do limite, e os casos válidos usam o valor exatamente no limite.

| Req. | Variável (limite) | Imediatamente fora | No limite | Justificativa |
|---|---|---|---|---|
| REQ-01 | Hóspedes, mínimo (1) | 0 → rejeitar (CT-009) | 1 → aceitar (CT-001) | Uma reserva precisa de ao menos um hóspede. |
| REQ-01 | Hóspedes, máximo somado (101+102: 5) | 6 → rejeitar (CT-010) | 5 → aceitar (CT-002) | Verifica se a capacidade é somada quando há vários quartos. |
| REQ-02 | Data de entrada (mín. = hoje) | D−1 → rejeitar (CT-013) | D → aceitar (CT-004) | O README exige "pelo menos hoje"; a fronteira passado/presente é onde se costuma errar comparando data com data-hora. |
| REQ-02 | Entrada × saída existente (12/03/2030) | entrada 11/03/2030 → conflito (CT-012) | entrada 12/03/2030 → livre (CT-003) | Com intervalo `[entrada, saída)`, entrar no dia em que o outro sai não conflita. |
| REQ-03 | Duração da reserva (mín. = 1 noite) | 0 → rejeitar (CT-015) | 1 → aceitar, custo 100 (CT-004) | Saída = entrada não gera diária; 2 noites custam 200 (CT-001). |

O limite simétrico "saída no dia da entrada de outra estadia" não entrou na etapa funcional; a mutação mostrou essa lacuna e ele foi acrescentado como ampliação do CT-003 (seção 7.3).

### 4.3 Casos funcionais e resultados no código original

«CASOS_FUNCIONAIS»

**Resultado (código original, `evidencias/funcional-original/`):** 15 casos, **6 passaram e 9 falharam** confirmando 9 defeitos dos três requisitos (DEF-01 a DEF-07, DEF-18 e DEF-19). As falhas têm causas distintas, conferidas com `--runxfail`: `KeyError: 'user_available'`, `ValueError` em `int('abc')`, `TypeError` em `combine(None)` e na comparação com `None`, além de redirecionamentos diferentes do oráculo. Por requisito (pelo requisito da classe principal de cada caso): REQ-01 com 11 casos, REQ-02 com 3 e REQ-03 com 1. Cobertura do recorte: **60/63 comandos (95,2%) e 29/34 desvios (85,3%)**.

## 5. Etapa 2: teste estrutural

### 5.1 Meta de cobertura e justificativa

**Critério:** todos-os-nós e todos-os-arcos (comandos e desvios, `coverage run --branch`) nas duas funções que implementam os três requisitos no original: `reserve` (reserva e validação das datas) e `cal_cost` (diárias entre entrada e saída), com «ORIG_CMD» comandos e «ORIG_DESV» desvios. **Meta: 100% dos comandos e 100% dos desvios viáveis.**

Justificativa:

1. O recorte é pequeno e concentra toda a regra de negócio testada, então a meta máxima tem custo baixo.
2. Cobertura de desvios subsume a de comandos e obriga a exercitar os ramos falsos (sessão encerrada, laço sem conflito), justamente onde a etapa funcional deixou lacunas.
3. Critérios mais fortes, como caminhos simples, explodem combinatoriamente por causa dos laços aninhados de `reserve` (três níveis) e trariam pouco ganho diante do teste de mutação da etapa seguinte.

A medição é restrita ao recorte porque medir `views.py` inteiro misturaria rotas deliberadamente não testadas (cadastro, login, consulta, alteração, pagamento) e tornaria qualquer meta global arbitrária.

### 5.2 Casos reaproveitados, lacunas e ampliações

Nenhum caso novo foi criado nesta etapa. Cinco casos funcionais foram reaproveitados para percorrer os grafos de fluxo de `reserve`, um para cada caminho principal da função: **CT-001** (reserva aceita), **CT-005** (sem login), **CT-009** (dado inválido), **CT-012** (quarto ocupado) e **CT-013** (data no passado). O V&V TestLab mostra, em cada grafo, os nós e arestas que cada caso executou.

As lacunas de cobertura foram fechadas **ampliando** três desses casos com o cenário que faltava. A ampliação é outra função pytest com o mesmo identificador e a marca `estrutural`.

| Trecho não coberto (original) | Por que ficou de fora | Caso ampliado |
|---|---|---|
| `reserve` 241 (desvio 189→241) | A etapa funcional só enviava o formulário (`POST`); nunca o abria (`GET`) com usuário autenticado | CT-001 |
| `reserve` desvios 208→205 e 205→204 (vínculo de outro quarto; fim do laço interno sem conflito) | Nos casos funcionais, todas as reservas prévias eram do mesmo quarto | CT-001 |
| `reserve` 242–243 (desvio 186→242, ramo falso de `if session['user_available']`) | O caso sem sessão não cria a chave, e o original lança `KeyError` antes do `if`; o ramo falso só roda com a chave valendo `False`, estado deixado pelo `logout` | CT-005 |
| `reserve` desvio 230→229 (`if each.rid > current_id` falso) | **Inviável:** os IDs vêm em ordem crescente de chave primária, então cada `rid` supera o máximo anterior | — |

A leitura do laço triplo para cobrir os desvios 208→205 e 205→204 expôs mais um defeito: o laço compara cada quarto reservado com as datas de todas as reservas, porque falta `brid == rid`. O CT-012 (quarto ocupado) foi ampliado com o cenário que prova isso e revelou o DEF-15.

| Ampliação | Classes | Cenário | Esperado | Original |
|---|---|---|---|---|
| CT-001 (estrutural) | CE-01, CE-15 | Bruno tem o 102 de 10/03/2030 a 12/03/2030; Ana abre o formulário e reserva o 101 nas mesmas datas | formulário exibido; reserva aceita | passou |
| CT-005 (estrutural) | CE-02 | `user_available = False` (depois de logout) em `GET` e `POST /reserve` | redireciona a `/`; nada gravado | passou |
| CT-012 (estrutural) | CE-15 | Ana tem o 101 de 10/03/2030 a 12/03/2030 e Bruno o 102 de 20/03/2030 a 22/03/2030; reservar o 101 de 20/03/2030 a 22/03/2030 | aceita | **falhou – DEF-15** (mascarado por DEF-01) |

**Resultado (código original, `evidencias/estrutural-original/`):** os mesmos 15 casos (18 funções pytest); 5 casos passaram e 10 falharam (xfail estrito). Cobertura do recorte: **63/63 comandos (100%) e 33/34 desvios (97,1%)**. A meta foi atingida, porque o desvio restante é inviável.

## 6. Correção dos defeitos antes da mutação

A mutação precisa de uma suíte que passe no programa mutado. Por isso os defeitos foram corrigidos **antes** de gerar os mutantes, em commits separados no fork, cada um citando a causa e os casos que o confirmam. O diff completo está em `evidencias/correcoes.diff` (`git diff sut-original sut-corrigido -- hotel`).

| Commit | Defeitos | Casos que passaram a passar |
|---|---|---|
| `8a6c4bd` | DEF-07 (sessão sem chave → `KeyError`) | CT-005 (e CT-102, complementar) |
| `2d1b2cd` | DEF-01 (tautologia), DEF-15 (produto cartesiano) | CT-003, CT-012 (ampliação) |
| `704bc86` | DEF-02 (entrada hoje) | CT-004 |
| `644fd0d` | DEF-03, 04, 05, 06, 18, 19 (validação da reserva; transação única) | CT-006, 007, 008, 009, 011, 014 |
| `1313f12` | DEF-08, 09, 10, 11 (RF-08 cancelamento, secundário; template com `POST`) | CT-103 a CT-106 (complementares) |
| `9e66e2d` | DEF-12, 13, 14, 16, 17, 18 (RF-04 consulta, secundário; filtro na sessão) | CT-112 a CT-116 (complementares) |

As mensagens desses commits citam a numeração de casos da primeira versão da suíte (seção 8). Em cada passo, a suíte inteira foi executada para confirmar que nenhum caso que já passava regrediu. **Resultado final no programa corrigido (tag `sut-corrigido`, `evidencias/suite-corrigida/`): 15/15 casos passaram** (18 funções pytest), sem `skip` nem `xfail`, com cobertura do recorte de **65/65 comandos e 28/28 desvios (100%)**. Os 14 complementares também passam. O código corrigido tem menos desvios que o original (28 contra 34) porque o laço triplo foi trocado por uma junção SQL e por compreensões de conjunto. As funções auxiliares (`_sessao_autenticada`, `_periodos_conflitam`, `_quartos_ocupados`, `_ler_quartos`) entram no recorte medido.

Um ajuste de oráculo foi necessário e está registrado no commit `8a6c4bd`. O CT-102 (complementar) esperava que o cancelamento sem sessão redirecionasse para `/`, mas o sistema redireciona para `/rooms`, que exige login e então leva a `/`. Isso não é defeito do software: o requisito verificado, preservar a reserva, não mudou.

## 7. Etapa 3: teste baseado em defeitos (mutação)

### 7.1 Configuração e escopo

* **Ferramenta:** Cosmic Ray 8.4.3, distribuidor local, timeout de 30 s por mutante e todos os operadores padrão: substituição de operadores relacionais, aritméticos, lógicos e unários, troca de números, de `break`/`continue` e de palavras-chave, laço de zero iterações, remoção de decorador etc.
* **Escopo:** **todos os mutantes** gerados nas linhas das funções dos três requisitos no `hotel/views.py` corrigido, sem amostragem: `reserve`, `cal_cost` e as quatro auxiliares. Total: **«MUT_TOTAL» mutantes**. As demais rotas, inclusive as dos requisitos secundários (`check_available`, `show_rooms` e `delete_reservation`), foram excluídas porque não fazem parte do recorte; incluí-las só acrescentaria sobreviventes triviais.
* **Configuração:** `mutacao/cosmic-ray-inicial.toml` e `mutacao/cosmic-ray-final.toml`. O comando de teste é `pytest -x -q`, restrito a `-m 'funcional or estrutural'` na rodada inicial e a `-m 'funcional or estrutural or mutacao'` na final (os complementares ficam de fora). O script `scripts/mutacao.py` monta a sessão, executa `cosmic-ray exec` e grava `sessao.sqlite`, `resumo.json`, `sobreviventes.txt` (diff de cada sobrevivente) e `execucao.txt`.
* **Escore:** escore de mutação (%) = mortos ÷ (total de mutantes gerados − mutantes equivalentes) × 100. Um mutante equivalente não muda o comportamento do programa, então nenhum teste consegue matá-lo; por isso ele sai do denominador. A equivalência é uma propriedade do mutante, identificada na análise dos sobreviventes (seção 7.2), e vale para as duas rodadas. Para comparação, também é informado o escore bruto (mortos ÷ gerados), que é o que o Cosmic Ray mostra. Não houve mutantes incompetentes nem *timeouts*.

### 7.2 Rodada inicial (suíte ao fim da etapa estrutural)

Os 15 casos (com as ampliações estruturais, 18 funções pytest) rodaram contra cada mutante. **141 mutantes: 127 mortos e 14 sobreviventes. «MUT_INI_ESCORE»** Execução em cerca de 4 minutos.

| # | Função (linha) | Mutação | Classificação | Ação |
|---|---|---|---|---|
| S1 | `_periodos_conflitam` (17) | `entrada_b < saida_a` → `<=` | **Não equivalente.** Nenhum caso tinha a nova estadia terminando no dia em que outra começa; a etapa funcional só testou o limite do outro lado (CT-003) | **ampliação do CT-003** |
| S2 | `_periodos_conflitam` (17) | `entrada_b < saida_a` → `is not` | **Não equivalente.** Mesmo cenário: entre objetos de data distintos, `is not` é sempre verdadeiro | **ampliação do CT-003** |
| S3 | `_periodos_conflitam` (17) | `entrada_b < saida_a` → `!=` | **Não equivalente.** Acusa conflito com qualquer estadia posterior não adjacente; nenhum caso reservava um período inteiramente anterior a uma reserva existente | **ampliação do CT-003** |
| S4 | `_quartos_ocupados` (23) | `Booked.brid == Reservations.rid` → `>=` | **Não equivalente.** Nenhum caso tinha um vínculo de reserva *posterior* capaz de herdar as datas de uma reserva *anterior* de outro quarto | **ampliação do CT-012** |
| S5 | `_ler_quartos` (34) | `set(numeros) <= existentes` → `<` | **Não equivalente.** Nenhum caso reservava *todos* os quartos do hotel | **ampliação do CT-002** |
| S6 | `reserve` (230) | `d2 <= d1` → `d2 == d1` | **Não equivalente.** A classe CE-22 (saída igual ou anterior à entrada) foi testada só com 0 noites; uma saída anterior à entrada passaria | **ampliação do CT-015** |
| S7 | `cal_cost` (268) | `each_room_id == e.room_number` → `is` | **Não equivalente.** `is` só coincide com `==` para inteiros de −5 a 256, que o CPython mantém em cache; nenhum caso reservava o quarto 301 | **ampliação do CT-002** |
| S8 | `reserve` (217) | `request.method == 'POST'` → `>=` | **Equivalente.** A rota só admite `GET`, `POST`, `HEAD` e `OPTIONS`, e nenhum método diferente de `POST` é ≥ `'POST'` na ordem lexicográfica | — |
| S9 | `reserve` (226) | `time(0, 0)` → `time(1, 0)` em `d1` | **Equivalente.** `d1` só é comparado com datas à meia-noite (`d2` e datas gravadas) e com `date.today()` via `d1.date()`; deslocar a hora de `d1` dentro do mesmo dia não inverte nenhuma comparação, e o valor gravado é `checkin`, não `d1` | — |
| S10 | `reserve` (226) | `time(0, 0)` → `time(0, 1)` | **Equivalente** (idem) | — |
| S11 | `reserve` (247) | custo inicial `0` → `1` | **Equivalente.** O valor é sobrescrito por `cal_cost` antes do único `commit` | — |
| S12 | `reserve` (247) | custo inicial `0` → `-1` | **Equivalente** (idem) | — |
| S13 | `_ler_quartos` (34) | `len(set(n)) != len(n)` → `<` | **Equivalente.** Um conjunto nunca tem mais elementos que a lista de origem, então `!=` e `<` são a mesma condição | — |
| S14 | `_ler_quartos` (34) | `len(set(n)) != len(n)` → `is not` | **Equivalente no domínio.** Os comprimentos só passam de 256 se o usuário informar mais de 256 quartos numa reserva, o que é irrealista; abaixo disso, o cache de inteiros do CPython torna `is not` idêntico a `!=` | — |

### 7.3 Casos ampliados e rodada final

Em vez de criar casos novos, os sobreviventes não equivalentes foram mortos **ampliando os casos que deveriam tê-los detectado** (funções com a marca `mutacao` e o mesmo identificador):

| Caso ampliado | Classes | Cenário acrescentado | Esperado | Mata |
|---|---|---|---|---|
| CT-002 | CE-05, CE-10, CE-11 | Reservar os três quartos (101, 102 e 301) para 9 hóspedes, de 10/03/2030 a 12/03/2030 | aceita; custo R$ 900; 3 vínculos | S5, S7 |
| CT-003 | CE-15, CE-21 | 101 ocupado de 10/03/2030 a 12/03/2030; reservar de 08/03/2030 a 10/03/2030 (sai no dia em que a outra entra) e de 05/03/2030 a 07/03/2030 | as duas aceitas | S1, S2, S3 |
| CT-012 | CE-15 | Ana tem o 102 de 10/03/2030 a 12/03/2030 (reserva 1); Bruno tem o 101 de 20/03/2030 a 22/03/2030 (reserva 2); Ana reserva o 101 de 10/03/2030 a 12/03/2030 | aceita | S4 |
| CT-015 | CE-22 | saída (09/03/2030) um dia antes da entrada (10/03/2030) | recusa | S6 |

**Rodada final (os mesmos 15 casos, 22 funções pytest, `evidencias/mutacao-final/`): «MUT_FINAL_TEXTO»

### 7.4 Fragilidades reveladas

A suíte tinha 100% de cobertura de desvios e, mesmo assim, deixou vivos 7 mutantes não equivalentes. As fragilidades expostas foram:

1. **Limite testado de um lado só.** A etapa funcional testou "entrar no dia em que a outra estadia sai", mas não o simétrico "sair no dia em que a outra entra", nem um período inteiramente anterior. Três mutantes do predicado de conflito sobreviveram por isso.
2. **Um único representante de uma classe inválida.** CE-22 (saída igual ou anterior à entrada) foi exercitada só com 0 noites. Trocar `<=` por `==` mantinha esse caso correto e deixava passar períodos negativos.
3. **Dados de teste pouco variados.** Nenhum caso reservava o quarto 301; os quartos usados (101 e 102) cabem no cache de inteiros pequenos do Python, o que esconde a troca de `==` por `is` no cálculo das diárias. Em produção, com quartos numerados acima de 256, esse erro passaria despercebido.
4. **Ordem de criação fixa e nenhum caso no extremo da enumeração de quartos.** Faltavam a reserva mais nova pertencendo ao quarto pedido (o que distingue `brid == rid` de uma junção errada) e uma reserva de todos os quartos.

Os 7 equivalentes vêm de código defensivo ou redundante que veio do original: o custo provisório 0, `time(0, 0)` explícito e a comparação de tamanhos em `_ler_quartos`. Eles mostram também por que a fórmula desconta os equivalentes: o escore bruto subestima a qualidade da suíte. Com os equivalentes fora do denominador, o escore final é «MUT_AJUSTADO»: todos os mutantes que podiam ser mortos foram mortos.

## 8. Evolução incremental

«EVOLUCAO»

A ordem **Funcional → Estrutural → (correção) → Mutação** está no histórico do fork: `afeb312` (etapa 1), `ac975b7` (etapa 2), seis commits de correção, e `324e29a` (etapa 3). Os commits posteriores reorganizaram o recorte. Na última revisão, a consulta de disponibilidade passou a requisito secundário, a suíte funcional foi enxugada para 15 casos (um por classe inválida, com os limites embutidos) e os casos foram renumerados. Todas as etapas foram então reexecutadas do zero, e as evidências deste relatório são dessa execução. Nessa versão, **os mesmos 15 casos atravessam as três etapas**: a estrutural e a de mutação não criaram casos, apenas ampliaram alguns deles (3 e 4 casos, respectivamente) com novas funções pytest de mesmo identificador. Nenhum caso foi removido ou marcado com `skip`. As datas fixas dos casos ficaram em março de 2030.

## 9. Registro de defeitos

Linhas referentes ao `hotel/views.py` original (`sut-original`). Todos os defeitos têm teste automatizado que falha no original e passa no corrigido. **DEF-08 a DEF-11 pertencem ao RF-08 (cancelamento) e DEF-12, DEF-13, DEF-14, DEF-16 e DEF-17 ao RF-04 (consulta)**, requisitos secundários, e foram revelados pelos testes complementares; os outros 10 pertencem aos três requisitos principais.

«DEFEITOS»

**Fora do recorte:** `update_reservation`, `about_user` e `payment` repetem a causa de DEF-07 (`session['user_available']`), e `update_reservation` repete a de DEF-01 e DEF-15. Eles não foram corrigidos nem testados por estarem fora do escopo. A correção seria a mesma, reutilizando `_sessao_autenticada` e `_quartos_ocupados`.

### 9.1 Testes complementares dos requisitos secundários (RF-08 cancelar e RF-04 consultar)

O cancelamento e a consulta de disponibilidade já fizeram parte do recorte em versões anteriores. Seus casos continuam executáveis em `tests/test_04_secundarios.py` (marca `secundario`), com as classes CE-31 a CE-47, mas ficam fora das métricas de cobertura e de mutação. Evidências: `evidencias/secundarios-original/` e `evidencias/secundarios-corrigida/`.

«CASOS_SECUNDARIOS»

## 10. Interpretação da cobertura e limitações

* **Cobertura não é ausência de defeitos.** Na etapa 2, o código original tinha 100% de comandos cobertos e 10 casos falhando. Em `reserve`, por exemplo, a linha do predicado tautológico era executada em todos os casos com reserva prévia e errava sempre que as estadias não se sobrepunham. Cobertura mede o que foi *executado*, não o que foi *verificado*. Quem revela o defeito é o oráculo.
* **Comandos × desvios.** Depois da etapa 1, a cobertura de comandos (95,2%) era 10 pontos maior que a de desvios (85,3%). Os desvios 205→204 e 208→205 estavam em linhas executadas, mas um dos lados da decisão nunca ocorreu. Esse lado era o caso "vínculo de outro quarto", que depois levou ao DEF-15.
* **Desvio inviável.** O 230→229 do original não pode ser coberto porque as consultas retornam as reservas em ordem de chave primária. A correção eliminou esse laço.
* **Global × recorte.** No `views.py` inteiro, a cobertura final é de «COV_VIEWS_TOTAL». O restante corresponde a rotas fora do escopo. É uma lacuna declarada, não um defeito da suíte.
* **100% de desvios ≠ suíte forte.** A etapa 3 mostrou 7 mutantes não equivalentes vivos com 100% de desvios.
* **Limitações.**
    * Os testes usam o cliente de teste do Flask e SQLite em memória: não há automação de navegador, carga ou concorrência real (duas reservas simultâneas do mesmo quarto não foram testadas).
    * A proteção CSRF não é validada pelas rotas do original; a correção de DEF-10 (`POST`) reduz o risco, mas não o elimina.
    * As senhas são gravadas em texto plano (`models.py`), fora do recorte.
    * Alguns oráculos são convenções declaradas (seção 3), não requisitos escritos pela autora.
    * O Cosmic Ray foi aplicado só às funções dos três requisitos; a consulta (RF-04) tem apenas testes complementares, e RF-07 (alteração) repete as regras de datas e não foi testado.

## 11. Conclusões e lições aprendidas

1. **A técnica funcional encontrou a maior parte dos defeitos** (9 dos 10 dos três requisitos) com 15 casos, sem olhar o código, porque cada classe inválida teve um caso próprio e os limites foram embutidos nesses casos. O limite "entrada hoje" e as estadias adjacentes expuseram defeitos que valores típicos não mostrariam.
2. **A técnica estrutural, reaproveitando 5 casos funcionais, encontrou o que a especificação não sugere:** o produto cartesiano entre reservas e vínculos (DEF-15). Ela também mostrou que um defeito pode ficar **mascarado** por outro (DEF-01), só aparecendo depois da primeira correção.
3. **A mutação avaliou os próprios testes.** Com 100% de desvios, a suíte ainda tinha fragilidades concretas (limite testado de um lado só, um único representante de classe inválida, dados homogêneos), corrigidas ampliando 4 dos 15 casos, sem criar casos novos.
4. **Corrigir antes de mutar é indispensável.** Mutar o original, com 10 testes falhando, invalidaria o escore, porque um mutante que "corrige" um defeito seria contado como vivo ou morto por acaso.
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

* `SUT_VERSAO=original pytest -m funcional -rxX` (15 casos; 9 falhas esperadas)
* `pytest -m 'funcional or estrutural or mutacao'` (os 15 casos com todas as ampliações: 22 funções)
* `pytest --cov=hotel.views --cov-branch --cov-report=term-missing`
* `.venv-mutation/Scripts/python.exe scripts/mutacao.py final`
* `git diff sut-original sut-corrigido -- hotel`

## Apêndice A: rastreabilidade classe → casos

«RASTREABILIDADE»
