# Rastreabilidade: classe de equivalência → casos de teste

| Classe | Req. | Condição | Tipo | Descrição | Casos funcionais | Outros casos |
|---|---|---|---|---|---|---|
| CE-01 | REQ-01 | C01 Sessão | válida | Usuário autenticado | CT-001 | CT-001 |
| CE-02 | REQ-01 | C01 Sessão | inválida | Sem sessão (nunca fez login) ou sessão encerrada | CT-005 | CT-005 |
| CE-03 | REQ-01 | C02 Formato dos quartos | válida | Números inteiros separados por vírgula | CT-001 | — |
| CE-04 | REQ-01 | C02 Formato dos quartos | inválida | Texto não numérico | CT-006 | — |
| CE-05 | REQ-01 | C03 Existência dos quartos | válida | Todos os quartos existem | CT-001 | CT-002 |
| CE-06 | REQ-01 | C03 Existência dos quartos | inválida | Algum quarto não existe | CT-007 | — |
| CE-07 | REQ-01 | C04 Repetição de quartos | válida | Sem repetição | CT-001 | — |
| CE-08 | REQ-01 | C04 Repetição de quartos | inválida | Quarto repetido | CT-008 | — |
| CE-09 | REQ-01 | C05 Quantidade de quartos | válida | Um quarto | CT-001 | — |
| CE-10 | REQ-01 | C05 Quantidade de quartos | válida | Vários quartos (custo e capacidade somados) | CT-002 | CT-002 |
| CE-11 | REQ-01 | C06 Nº de hóspedes | válida | Inteiro de 1 até a capacidade somada dos quartos | CT-001, CT-002 | CT-002 |
| CE-12 | REQ-01 | C06 Nº de hóspedes | inválida | Menor que 1 | CT-009 | — |
| CE-13 | REQ-01 | C06 Nº de hóspedes | inválida | Maior que a capacidade somada | CT-010 | — |
| CE-14 | REQ-01 | C06 Nº de hóspedes | inválida | Não inteiro (texto) | CT-011 | — |
| CE-15 | REQ-01 | C07 Ocupação do quarto no período | válida | Nenhuma estadia do quarto com interseção (inclui estadias adjacentes e reservas de outros quartos) | CT-001, CT-003 | CT-001, CT-012, CT-003, CT-012 |
| CE-16 | REQ-01 | C07 Ocupação do quarto no período | inválida | Estadia existente do quarto com interseção de ao menos uma noite | CT-012 | — |
| CE-17 | REQ-02 | C08 Entrada em relação a hoje | válida | Hoje ou data futura | CT-001, CT-003, CT-004 | — |
| CE-18 | REQ-02 | C08 Entrada em relação a hoje | inválida | Data passada | CT-013 | — |
| CE-19 | REQ-02 | C09 Formato das datas | válida | Entrada e saída válidas no formato MM/DD/AAAA | CT-001 | — |
| CE-20 | REQ-02 | C09 Formato das datas | inválida | Data malformada, inexistente ou ausente | CT-014 | — |
| CE-21 | REQ-03 | C10 Duração da reserva (saída − entrada) | válida | 1 noite ou mais; cada noite é uma diária cobrada | CT-001, CT-004 | CT-003 |
| CE-22 | REQ-03 | C10 Duração da reserva (saída − entrada) | inválida | 0 noites ou negativa (saída igual ou anterior à entrada) | CT-015 | CT-015 |
| CE-31 | RF-08 | S1 Sessão | válida | Usuário autenticado | CT-101, CT-106, CT-107 | — |
| CE-32 | RF-08 | S1 Sessão | inválida | Sem sessão ou sessão encerrada | CT-102 | — |
| CE-33 | RF-08 | S2 Existência da reserva | válida | Reserva existente | CT-101, CT-106, CT-107 | — |
| CE-34 | RF-08 | S2 Existência da reserva | inválida | Identificador inexistente | CT-103 | — |
| CE-35 | RF-08 | S3 Titularidade | válida | Reserva do próprio usuário | CT-101, CT-106, CT-107 | — |
| CE-36 | RF-08 | S3 Titularidade | inválida | Reserva de outro usuário | CT-104, CT-108 | — |
| CE-37 | RF-08 | S4 Forma da requisição | válida | Confirmação explícita (POST) | CT-101, CT-106, CT-107 | — |
| CE-38 | RF-08 | S4 Forma da requisição | inválida | Navegação por link (GET) | CT-105 | — |
| CE-39 | RF-08 | S5 Registros dependentes | válida | Reserva sem pagamento | CT-101 | — |
| CE-40 | RF-08 | S5 Registros dependentes | válida | Reserva com pagamento registrado | CT-106 | — |
| CE-41 | RF-04 | Q1 Período da consulta | válida | Saída posterior à entrada | CT-111 | — |
| CE-42 | RF-04 | Q1 Período da consulta | inválida | Saída igual ou anterior à entrada | CT-112 | — |
| CE-43 | RF-04 | Q2 Hóspedes na consulta | válida | Inteiro maior ou igual a 1 | CT-111 | — |
| CE-44 | RF-04 | Q2 Hóspedes na consulta | inválida | Menor que 1 | CT-113 | — |
| CE-45 | RF-04 | Q3 Quarto no resultado | válida | Livre no período e com capacidade: exibido | CT-111 | — |
| CE-46 | RF-04 | Q3 Quarto no resultado | válida | Ocupado no período ou sem capacidade: omitido | CT-111, CT-114, CT-116 | — |
| CE-47 | RF-04 | Q4 Filtro entre sessões | válida | O filtro de um usuário não altera a lista de outro | CT-115 | — |

| Caso | Etapa | Classes | Defeito revelado no original |
|---|---|---|---|
| CT-001 | funcional | CE-01, CE-03, CE-05, CE-07, CE-09, CE-11, CE-15, CE-17, CE-19, CE-21 | — |
| CT-001 | estrutural | CE-01, CE-15 | — |
| CT-002 | funcional | CE-10, CE-11 | — |
| CT-002 | mutacao | CE-05, CE-10, CE-11 | — |
| CT-003 | funcional | CE-15, CE-17 | DEF-01 |
| CT-003 | mutacao | CE-15, CE-21 | — |
| CT-004 | funcional | CE-17, CE-21 | DEF-02 |
| CT-005 | funcional | CE-02 | DEF-07 |
| CT-005 | estrutural | CE-02 | — |
| CT-006 | funcional | CE-04 | DEF-04 |
| CT-007 | funcional | CE-06 | DEF-05 |
| CT-008 | funcional | CE-08 | DEF-06 |
| CT-009 | funcional | CE-12 | DEF-03 |
| CT-010 | funcional | CE-13 | — |
| CT-011 | funcional | CE-14 | DEF-19 |
| CT-012 | funcional | CE-16 | — |
| CT-012 | estrutural | CE-15 | DEF-15 |
| CT-012 | mutacao | CE-15 | — |
| CT-013 | funcional | CE-18 | — |
| CT-014 | funcional | CE-20 | DEF-18 |
| CT-015 | funcional | CE-22 | — |
| CT-015 | mutacao | CE-22 | — |
| CT-101 | secundario | CE-31, CE-33, CE-35, CE-37, CE-39 | — |
| CT-102 | secundario | CE-32 | DEF-07 |
| CT-103 | secundario | CE-34 | DEF-09 |
| CT-104 | secundario | CE-36 | DEF-08 |
| CT-105 | secundario | CE-38 | DEF-10 |
| CT-106 | secundario | CE-31, CE-33, CE-35, CE-37, CE-40 | DEF-11 |
| CT-107 | secundario | CE-31, CE-33, CE-35, CE-37 | — |
| CT-108 | secundario | CE-36 | DEF-08 |
| CT-111 | secundario | CE-41, CE-43, CE-45, CE-46 | — |
| CT-112 | secundario | CE-42 | DEF-12 |
| CT-113 | secundario | CE-44 | DEF-13 |
| CT-114 | secundario | CE-46 | DEF-14 |
| CT-115 | secundario | CE-47 | DEF-16 |
| CT-116 | secundario | CE-46 | DEF-17 |
