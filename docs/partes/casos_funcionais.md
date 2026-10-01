Legenda: **P** = passou no original; **F** = falhou no original, confirmando o defeito indicado (xfail estrito). No código corrigido, todos passam. Valores não citados usam o padrão dos testes: quarto 101, 2 hóspedes, de 10/03/2030 a 12/03/2030. "Hoje" e "ontem" são relativos ao dia da execução.

| Caso | Classes | Entrada / cenário | Resultado esperado | Original |
|---|---|---|---|---|
| CT-001 | CE-01, 03, 05, 07, 09, 11, 15, 17, 19, 21 | 101, 1 hóspede, de 10/03/2030 a 12/03/2030 | redireciona a `/rooms`; custo R$ 200; vínculo (reserva, 101) | P |
| CT-002 | CE-10, CE-11 | 101 e 102; 5 hóspedes (= capacidade somada); de 10/03/2030 a 13/03/2030 | aceita; custo (100+150)×3 = R$ 750 | P |
| CT-003 | CE-15, CE-17 | 101 ocupado de 10/03/2030 a 12/03/2030; nova reserva de 12/03/2030 a 14/03/2030 (entra no dia da saída) | aceita | F – DEF-01 |
| CT-004 | CE-17, CE-21 | entrada hoje, saída amanhã (1 noite) | aceita; custo R$ 100 | F – DEF-02 |
| CT-005 | CE-02 | visitante sem login: `GET` e `POST /reserve` | redireciona a `/`; nada gravado | F – DEF-07 |
| CT-006 | CE-04 | quartos `abc` | recusa (`/reserve`), nada gravado | F – DEF-04 |
| CT-007 | CE-06 | quartos `101,999`, 2 hóspedes | recusa; nenhum vínculo | F – DEF-05 |
| CT-008 | CE-08 | quartos `101,101` | recusa | F – DEF-06 |
| CT-009 | CE-12 | 0 hóspedes | recusa | F – DEF-03 |
| CT-010 | CE-13 | 101 e 102 com 6 hóspedes (capacidade 5) | recusa | P |
| CT-011 | CE-14 | hóspedes `dois` | recusa | F – DEF-19 |
| CT-012 | CE-16 | 101 ocupado de 10/03/2030 a 12/03/2030; nova reserva de 11/03/2030 a 13/03/2030 | recusa | P |
| CT-013 | CE-18 | entrada ontem | recusa | P |
| CT-014 | CE-20 | entrada `2030-13-01` | recusa | F – DEF-18 |
| CT-015 | CE-22 | saída = entrada (10/03/2030, 0 noites) | recusa | P |
