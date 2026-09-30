# Rastreabilidade: classe de equivalência → casos de teste

| Classe | Req. | Condição | Tipo | Descrição | Casos funcionais | Outros casos |
|---|---|---|---|---|---|---|
| CE-01 | REQ-01 | C01 Sessão | válida | Usuário autenticado | CT-001 | CT-050 |
| CE-02 | REQ-01 | C01 Sessão | inválida | Sem sessão (nunca fez login) ou sessão encerrada | CT-014 | CT-048 |
| CE-11 | REQ-01 | C02 Formato dos quartos | válida | Números inteiros separados por vírgula | CT-001 | — |
| CE-12 | REQ-01 | C02 Formato dos quartos | inválida | Texto não numérico | CT-015 | — |
| CE-13 | REQ-01 | C03 Existência dos quartos | válida | Todos os quartos existem | CT-001 | CT-056 |
| CE-14 | REQ-01 | C03 Existência dos quartos | inválida | Algum quarto não existe | CT-016 | — |
| CE-15 | REQ-01 | C04 Repetição de quartos | válida | Sem repetição | CT-001 | — |
| CE-16 | REQ-01 | C04 Repetição de quartos | inválida | Quarto repetido | CT-017 | — |
| CE-19 | REQ-01 | C05 Quantidade de quartos | válida | Um quarto | CT-001 | CT-044, CT-059 |
| CE-20 | REQ-01 | C05 Quantidade de quartos | válida | Vários quartos (custo e capacidade somados) | CT-002, CT-060, CT-067 | CT-056 |
| CE-08 | REQ-01 | C06 Nº de hóspedes na reserva | válida | Inteiro de 1 até a capacidade somada dos quartos | CT-001, CT-002, CT-003, CT-006, CT-060 | — |
| CE-09 | REQ-01 | C06 Nº de hóspedes na reserva | inválida | Menor que 1 | CT-007 | — |
| CE-10 | REQ-01 | C06 Nº de hóspedes na reserva | inválida | Maior que a capacidade somada | CT-004, CT-005 | — |
| CE-45 | REQ-01 | C06 Nº de hóspedes na reserva | inválida | Não inteiro (texto) | CT-052 | — |
| CE-17 | REQ-01 | C07 Ocupação do quarto no período | válida | Nenhuma reserva do quarto com interseção (inclui estadias adjacentes e outros quartos) | CT-001, CT-021, CT-022, CT-023, CT-061, CT-062 | CT-044, CT-045, CT-055 |
| CE-18 | REQ-01 | C07 Ocupação do quarto no período | inválida | Reserva existente do quarto com interseção de ao menos uma noite | CT-018, CT-019, CT-020 | — |
| CE-31 | REQ-01 | C08 Sessão na consulta prévia | válida | Usuário autenticado | CT-030, CT-032 | CT-049 |
| CE-32 | REQ-01 | C08 Sessão na consulta prévia | inválida | Sem sessão ou sessão encerrada | CT-031 | CT-048 |
| CE-33 | REQ-01 | C09 Filtro da consulta | válida | Sem filtro: lista geral de quartos | CT-030 | CT-046 |
| CE-34 | REQ-01 | C09 Filtro da consulta | válida | Com período e hóspedes informados | CT-032 | — |
| CE-37 | REQ-01 | C10 Nº de hóspedes na consulta | válida | Inteiro maior ou igual a 1 | CT-032, CT-042 | — |
| CE-38 | REQ-01 | C10 Nº de hóspedes na consulta | inválida | Menor que 1 | CT-039 | — |
| CE-48 | REQ-01 | C10 Nº de hóspedes na consulta | inválida | Não inteiro (texto) | CT-054 | — |
| CE-39 | REQ-01 | C11 Ocupação de cada quarto na consulta | válida | Livre no período: exibido | CT-032, CT-033, CT-034, CT-035, CT-063, CT-064 | — |
| CE-40 | REQ-01 | C11 Ocupação de cada quarto na consulta | válida | Ocupado no período: omitido | CT-032, CT-036 | CT-047 |
| CE-41 | REQ-01 | C12 Capacidade de cada quarto na consulta | válida | Capacidade ≥ hóspedes: exibido | CT-032, CT-040, CT-042 | — |
| CE-42 | REQ-01 | C12 Capacidade de cada quarto na consulta | válida | Capacidade < hóspedes: omitido | CT-041 | — |
| CE-03 | REQ-02 | C13 Entrada em relação a hoje | válida | Hoje ou data futura | CT-001, CT-011, CT-012 | — |
| CE-04 | REQ-02 | C13 Entrada em relação a hoje | inválida | Data passada | CT-013 | — |
| CE-43 | REQ-02 | C14 Formato da data de entrada | válida | Data válida no formato MM/DD/AAAA (reserva ou consulta) | CT-001, CT-032 | — |
| CE-44 | REQ-02 | C14 Formato da data de entrada | inválida | Data malformada, inexistente ou ausente | CT-051, CT-053, CT-068 | — |
| CE-52 | REQ-02 | C15 Entrada × saída de estadia existente do quarto | válida | Entrada no dia da saída existente ou depois | CT-022, CT-034, CT-062, CT-064 | — |
| CE-53 | REQ-02 | C15 Entrada × saída de estadia existente do quarto | inválida | Entrada antes da saída existente, sobrepondo a estadia | CT-020, CT-036 | — |
| CE-05 | REQ-03 | C16 Duração da reserva (saída − entrada) | válida | 1 noite ou mais; cada noite é uma diária cobrada | CT-001, CT-008, CT-067 | CT-059 |
| CE-06 | REQ-03 | C16 Duração da reserva (saída − entrada) | inválida | 0 noites (saída = entrada) | CT-009 | — |
| CE-07 | REQ-03 | C16 Duração da reserva (saída − entrada) | inválida | Negativa (saída antes da entrada) | CT-010 | — |
| CE-35 | REQ-03 | C17 Período da consulta | válida | Saída posterior à entrada (1 noite ou mais) | CT-032, CT-043 | — |
| CE-36 | REQ-03 | C17 Período da consulta | inválida | Saída igual ou anterior à entrada | CT-037, CT-038 | — |
| CE-49 | REQ-03 | C18 Formato da data de saída | válida | Data válida no formato MM/DD/AAAA (reserva ou consulta) | CT-001, CT-032, CT-067 | — |
| CE-50 | REQ-03 | C18 Formato da data de saída | inválida | Data malformada ou inexistente | CT-065, CT-066 | — |
| CE-54 | REQ-03 | C19 Saída × entrada de estadia existente do quarto | válida | Saída no dia da entrada existente ou antes | CT-021, CT-035, CT-061, CT-063 | — |
| CE-55 | REQ-03 | C19 Saída × entrada de estadia existente do quarto | inválida | Saída depois da entrada existente, sobrepondo a estadia | CT-019 | — |
| CE-21 | RF-08 | S1 Sessão | válida | Usuário autenticado | CT-024, CT-029, CT-057 | — |
| CE-22 | RF-08 | S1 Sessão | inválida | Sem sessão ou sessão encerrada | CT-025 | — |
| CE-23 | RF-08 | S2 Existência da reserva | válida | Reserva existente | CT-024, CT-029, CT-057 | — |
| CE-24 | RF-08 | S2 Existência da reserva | inválida | Identificador inexistente | CT-026 | — |
| CE-25 | RF-08 | S3 Titularidade | válida | Reserva do próprio usuário | CT-024, CT-029, CT-057 | — |
| CE-26 | RF-08 | S3 Titularidade | inválida | Reserva de outro usuário | CT-027, CT-058 | — |
| CE-27 | RF-08 | S4 Forma da requisição | válida | Confirmação explícita (POST) | CT-024, CT-029, CT-057 | — |
| CE-28 | RF-08 | S4 Forma da requisição | inválida | Navegação por link (GET) | CT-028 | — |
| CE-29 | RF-08 | S5 Registros dependentes | válida | Reserva sem pagamento | CT-024 | — |
| CE-30 | RF-08 | S5 Registros dependentes | válida | Reserva com pagamento registrado | CT-029 | — |

| Caso | Etapa | Classes | Defeito revelado no original |
|---|---|---|---|
| CT-001 | funcional | CE-01, CE-03, CE-05, CE-08, CE-11, CE-13, CE-15, CE-17, CE-19, CE-43, CE-49 | — |
| CT-002 | funcional | CE-08, CE-20 | — |
| CT-003 | funcional | CE-08 | — |
| CT-004 | funcional | CE-10 | — |
| CT-005 | funcional | CE-10 | — |
| CT-006 | funcional | CE-08 | — |
| CT-007 | funcional | CE-09 | DEF-03 |
| CT-008 | funcional | CE-05 | — |
| CT-009 | funcional | CE-06 | — |
| CT-010 | funcional | CE-07 | — |
| CT-011 | funcional | CE-03 | DEF-02 |
| CT-012 | funcional | CE-03 | — |
| CT-013 | funcional | CE-04 | — |
| CT-014 | funcional | CE-02 | DEF-07 |
| CT-015 | funcional | CE-12 | DEF-04 |
| CT-016 | funcional | CE-14 | DEF-05 |
| CT-017 | funcional | CE-16 | DEF-06 |
| CT-018 | funcional | CE-18 | — |
| CT-019 | funcional | CE-18, CE-55 | — |
| CT-020 | funcional | CE-18, CE-53 | — |
| CT-021 | funcional | CE-17, CE-54 | DEF-01 |
| CT-022 | funcional | CE-17, CE-52 | DEF-01 |
| CT-023 | funcional | CE-17 | DEF-01 |
| CT-024 | secundario | CE-21, CE-23, CE-25, CE-27, CE-29 | — |
| CT-025 | secundario | CE-22 | DEF-07 |
| CT-026 | secundario | CE-24 | DEF-09 |
| CT-027 | secundario | CE-26 | DEF-08 |
| CT-028 | secundario | CE-28 | DEF-10 |
| CT-029 | secundario | CE-21, CE-23, CE-25, CE-27, CE-30 | DEF-11 |
| CT-030 | funcional | CE-31, CE-33 | — |
| CT-031 | funcional | CE-32 | DEF-07 |
| CT-032 | funcional | CE-31, CE-34, CE-35, CE-37, CE-39, CE-40, CE-41, CE-43, CE-49 | — |
| CT-033 | funcional | CE-39 | DEF-01 |
| CT-034 | funcional | CE-39, CE-52 | DEF-01 |
| CT-035 | funcional | CE-39, CE-54 | DEF-01 |
| CT-036 | funcional | CE-40, CE-53 | — |
| CT-037 | funcional | CE-36 | DEF-12 |
| CT-038 | funcional | CE-36 | DEF-12 |
| CT-039 | funcional | CE-38 | DEF-13 |
| CT-040 | funcional | CE-41 | — |
| CT-041 | funcional | CE-42 | DEF-14 |
| CT-042 | funcional | CE-37, CE-41 | — |
| CT-043 | funcional | CE-35 | — |
| CT-044 | estrutural | CE-17, CE-19 | — |
| CT-045 | estrutural | CE-17 | DEF-15 |
| CT-046 | estrutural | CE-33 | DEF-16 |
| CT-047 | estrutural | CE-40 | DEF-17 |
| CT-048 | estrutural | CE-02, CE-32 | — |
| CT-049 | estrutural | CE-31 | — |
| CT-050 | estrutural | CE-01 | — |
| CT-051 | funcional | CE-44 | DEF-18 |
| CT-052 | funcional | CE-45 | DEF-19 |
| CT-053 | funcional | CE-44 | DEF-18 |
| CT-054 | funcional | CE-48 | DEF-13 |
| CT-055 | mutacao | CE-17 | — |
| CT-056 | mutacao | CE-13, CE-20 | — |
| CT-057 | secundario | CE-21, CE-23, CE-25, CE-27 | — |
| CT-058 | secundario | CE-26 | DEF-08 |
| CT-059 | mutacao | CE-05, CE-19 | — |
| CT-060 | funcional | CE-08, CE-20 | — |
| CT-061 | funcional | CE-17, CE-54 | DEF-01 |
| CT-062 | funcional | CE-17, CE-52 | DEF-01 |
| CT-063 | funcional | CE-39, CE-54 | DEF-01 |
| CT-064 | funcional | CE-39, CE-52 | DEF-01 |
| CT-065 | funcional | CE-50 | DEF-18 |
| CT-066 | funcional | CE-50 | DEF-18 |
| CT-067 | funcional | CE-05, CE-20, CE-49 | — |
| CT-068 | funcional | CE-44 | DEF-18 |
