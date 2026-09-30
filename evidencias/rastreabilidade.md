# Rastreabilidade: classe de equivalência → casos de teste

| Classe | Req. | Condição | Tipo | Descrição | Casos funcionais | Outros casos |
|---|---|---|---|---|---|---|
| CE-01 | REQ-01 | C01 Sessão | válida | Usuário autenticado | CT-001 | CT-050 |
| CE-02 | REQ-01 | C01 Sessão | inválida | Sem sessão (nunca fez login) ou sessão encerrada | CT-014 | CT-048 |
| CE-03 | REQ-01 | C02 Data de entrada | válida | Hoje ou data futura | CT-001, CT-011, CT-012 | — |
| CE-04 | REQ-01 | C02 Data de entrada | inválida | Data passada | CT-013 | — |
| CE-05 | REQ-01 | C03 Duração (saída − entrada) | válida | 1 noite ou mais | CT-001, CT-008 | CT-059 |
| CE-06 | REQ-01 | C03 Duração (saída − entrada) | inválida | 0 noites (saída = entrada) | CT-009 | — |
| CE-07 | REQ-01 | C03 Duração (saída − entrada) | inválida | Negativa (saída antes da entrada) | CT-010 | — |
| CE-08 | REQ-01 | C04 Nº de hóspedes | válida | Inteiro de 1 até a capacidade somada dos quartos | CT-001, CT-002, CT-003, CT-006, CT-060 | — |
| CE-09 | REQ-01 | C04 Nº de hóspedes | inválida | Menor que 1 | CT-007 | — |
| CE-10 | REQ-01 | C04 Nº de hóspedes | inválida | Maior que a capacidade somada | CT-004, CT-005 | — |
| CE-45 | REQ-01 | C04 Nº de hóspedes | inválida | Não inteiro (texto) | CT-052 | — |
| CE-11 | REQ-01 | C05 Formato dos quartos | válida | Números inteiros separados por vírgula | CT-001 | — |
| CE-12 | REQ-01 | C05 Formato dos quartos | inválida | Texto não numérico | CT-015 | — |
| CE-13 | REQ-01 | C06 Existência dos quartos | válida | Todos os quartos existem | CT-001 | CT-056 |
| CE-14 | REQ-01 | C06 Existência dos quartos | inválida | Algum quarto não existe | CT-016 | — |
| CE-15 | REQ-01 | C07 Repetição de quartos | válida | Sem repetição | CT-001 | — |
| CE-16 | REQ-01 | C07 Repetição de quartos | inválida | Quarto repetido | CT-017 | — |
| CE-17 | REQ-01 | C08 Ocupação no período | válida | Nenhuma reserva do quarto com interseção (inclui estadias adjacentes) | CT-001, CT-021, CT-022, CT-023, CT-061, CT-062 | CT-044, CT-045, CT-055 |
| CE-18 | REQ-01 | C08 Ocupação no período | inválida | Reserva existente do quarto com interseção de ao menos uma noite | CT-018, CT-019, CT-020 | — |
| CE-19 | REQ-01 | C09 Quantidade de quartos | válida | Um quarto | CT-001 | CT-044, CT-059 |
| CE-20 | REQ-01 | C09 Quantidade de quartos | válida | Vários quartos (custo e capacidade somados) | CT-002, CT-060 | CT-056 |
| CE-43 | REQ-01 | C10 Formato das datas | válida | Datas válidas no formato MM/DD/AAAA | CT-001 | — |
| CE-44 | REQ-01 | C10 Formato das datas | inválida | Data malformada ou inexistente | CT-051 | — |
| CE-21 | REQ-02 | C11 Sessão | válida | Usuário autenticado | CT-024, CT-029 | CT-057 |
| CE-22 | REQ-02 | C11 Sessão | inválida | Sem sessão ou sessão encerrada | CT-025 | CT-048 |
| CE-23 | REQ-02 | C12 Existência da reserva | válida | Reserva existente | CT-024, CT-029 | CT-057 |
| CE-24 | REQ-02 | C12 Existência da reserva | inválida | Identificador inexistente | CT-026 | — |
| CE-25 | REQ-02 | C13 Titularidade | válida | Reserva do próprio usuário | CT-024, CT-029 | CT-057 |
| CE-26 | REQ-02 | C13 Titularidade | inválida | Reserva de outro usuário | CT-027 | CT-058 |
| CE-27 | REQ-02 | C14 Forma da requisição | válida | Confirmação explícita (POST) | CT-024, CT-029 | CT-057 |
| CE-28 | REQ-02 | C14 Forma da requisição | inválida | Navegação por link (GET) | CT-028 | — |
| CE-29 | REQ-02 | C15 Registros dependentes | válida | Reserva sem pagamento | CT-024 | — |
| CE-30 | REQ-02 | C15 Registros dependentes | válida | Reserva com pagamento registrado | CT-029 | — |
| CE-31 | REQ-03 | C16 Sessão | válida | Usuário autenticado | CT-030, CT-032 | CT-049 |
| CE-32 | REQ-03 | C16 Sessão | inválida | Sem sessão ou sessão encerrada | CT-031 | CT-048 |
| CE-33 | REQ-03 | C17 Filtro | válida | Sem filtro: lista geral de quartos | CT-030 | CT-046 |
| CE-34 | REQ-03 | C17 Filtro | válida | Com período e hóspedes informados | CT-032 | — |
| CE-35 | REQ-03 | C18 Período | válida | Entrada anterior à saída (1 noite ou mais) | CT-032, CT-043 | — |
| CE-36 | REQ-03 | C18 Período | inválida | Entrada igual ou posterior à saída | CT-037, CT-038 | — |
| CE-46 | REQ-03 | C19 Formato das datas | válida | Datas válidas no formato MM/DD/AAAA | CT-032 | — |
| CE-47 | REQ-03 | C19 Formato das datas | inválida | Data malformada ou inexistente | CT-053 | — |
| CE-37 | REQ-03 | C20 Nº de hóspedes | válida | Inteiro maior ou igual a 1 | CT-032, CT-042 | — |
| CE-38 | REQ-03 | C20 Nº de hóspedes | inválida | Menor que 1 | CT-039 | — |
| CE-48 | REQ-03 | C20 Nº de hóspedes | inválida | Não inteiro (texto) | CT-054 | — |
| CE-39 | REQ-03 | C21 Ocupação de cada quarto | válida | Livre no período: exibido | CT-032, CT-033, CT-034, CT-035, CT-063, CT-064 | — |
| CE-40 | REQ-03 | C21 Ocupação de cada quarto | válida | Ocupado no período: omitido | CT-032, CT-036 | CT-047 |
| CE-41 | REQ-03 | C22 Capacidade de cada quarto | válida | Capacidade ≥ hóspedes: exibido | CT-032, CT-040, CT-042 | — |
| CE-42 | REQ-03 | C22 Capacidade de cada quarto | válida | Capacidade < hóspedes: omitido | CT-041 | — |

| Caso | Etapa | Classes | Defeito revelado no original |
|---|---|---|---|
| CT-001 | funcional | CE-01, CE-03, CE-05, CE-08, CE-11, CE-13, CE-15, CE-17, CE-19, CE-43 | — |
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
| CT-019 | funcional | CE-18 | — |
| CT-020 | funcional | CE-18 | — |
| CT-021 | funcional | CE-17 | DEF-01 |
| CT-022 | funcional | CE-17 | DEF-01 |
| CT-023 | funcional | CE-17 | DEF-01 |
| CT-024 | funcional | CE-21, CE-23, CE-25, CE-27, CE-29 | — |
| CT-025 | funcional | CE-22 | DEF-07 |
| CT-026 | funcional | CE-24 | DEF-09 |
| CT-027 | funcional | CE-26 | DEF-08 |
| CT-028 | funcional | CE-28 | DEF-10 |
| CT-029 | funcional | CE-21, CE-23, CE-25, CE-27, CE-30 | DEF-11 |
| CT-030 | funcional | CE-31, CE-33 | — |
| CT-031 | funcional | CE-32 | DEF-07 |
| CT-032 | funcional | CE-31, CE-34, CE-35, CE-37, CE-39, CE-40, CE-41, CE-46 | — |
| CT-033 | funcional | CE-39 | DEF-01 |
| CT-034 | funcional | CE-39 | DEF-01 |
| CT-035 | funcional | CE-39 | DEF-01 |
| CT-036 | funcional | CE-40 | — |
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
| CT-048 | estrutural | CE-02, CE-22, CE-32 | — |
| CT-049 | estrutural | CE-31 | — |
| CT-050 | estrutural | CE-01 | — |
| CT-051 | funcional | CE-44 | DEF-18 |
| CT-052 | funcional | CE-45 | DEF-19 |
| CT-053 | funcional | CE-47 | DEF-18 |
| CT-054 | funcional | CE-48 | DEF-13 |
| CT-055 | mutacao | CE-17 | — |
| CT-056 | mutacao | CE-13, CE-20 | — |
| CT-057 | mutacao | CE-21, CE-23, CE-25, CE-27 | — |
| CT-058 | mutacao | CE-26 | — |
| CT-059 | mutacao | CE-05, CE-19 | — |
| CT-060 | funcional | CE-08, CE-20 | — |
| CT-061 | funcional | CE-17 | DEF-01 |
| CT-062 | funcional | CE-17 | DEF-01 |
| CT-063 | funcional | CE-39 | DEF-01 |
| CT-064 | funcional | CE-39 | DEF-01 |
