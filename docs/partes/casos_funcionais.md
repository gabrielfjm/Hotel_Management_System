Legenda: **P** = passou no original; **F** = falhou no original, confirmando o defeito indicado (xfail estrito). No código corrigido, todos passam.

| Caso | Classes | Entrada / cenário | Resultado esperado | Original |
|---|---|---|---|---|
| CT-001 | CE-01,03,05,08,11,13,15,17,19,43 | 101, 2 hóspedes, D+10 a D+12 | redireciona a `/rooms`; custo 200; vínculo (rid, 101) | P |
| CT-002 | CE-08, CE-20 | 101,102; 5 hóspedes; 3 noites | aceita; custo (100+150)×3 = 750 | P |
| CT-003 | CE-08 | 101 com 2 hóspedes (= capacidade) | aceita | P |
| CT-004 | CE-10 | 101 com 3 hóspedes | recusa (`/reserve`), nada gravado | P |
| CT-005 | CE-10 | 101,102 com 6 hóspedes (capacidade 5) | recusa | P |
| CT-006 | CE-08 | 1 hóspede | aceita | P |
| CT-007 | CE-09 | 0 hóspedes | recusa | F – DEF-03 |
| CT-008 | CE-05 | 1 noite | aceita; custo 100 | P |
| CT-009 | CE-06 | saída = entrada | recusa | P |
| CT-010 | CE-07 | saída = entrada − 1 | recusa | P |
| CT-011 | CE-03 | entrada hoje, 1 noite | aceita | F – DEF-02 |
| CT-012 | CE-03 | entrada amanhã | aceita | P |
| CT-013 | CE-04 | entrada ontem | recusa | P |
| CT-014 | CE-02 | visitante sem login: `GET` e `POST /reserve` | redireciona a `/`; nada gravado | F – DEF-07 |
| CT-015 | CE-12 | quartos `abc` | recusa | F – DEF-04 |
| CT-016 | CE-14 | quartos `101,999`, 2 hóspedes | recusa; nenhum vínculo | F – DEF-05 |
| CT-017 | CE-16 | quartos `101,101` | recusa | F – DEF-06 |
| CT-018 | CE-18 | 101 já reservado em D+10–12; nova D+10–12 | recusa | P |
| CT-019 | CE-18 | idem; nova D+9–11 | recusa | P |
| CT-020 | CE-18 | idem; nova D+11–13 | recusa | P |
| CT-021 | CE-17 | idem; nova D+8–10 | aceita | F – DEF-01 |
| CT-022 | CE-17 | idem; nova D+12–14 | aceita | F – DEF-01 |
| CT-023 | CE-17 | idem; nova D+20–22 | aceita | F – DEF-01 |
| CT-024 | CE-21,23,25,27,29 | Ana cancela a própria reserva (`POST`) | `/rooms`; reserva e vínculo removidos | P |
| CT-025 | CE-22 | visitante sem login `POST /delete/<rid>` | redireciona; reserva mantida | F – DEF-07 |
| CT-026 | CE-24 | `POST /delete/999` | 404 | F – DEF-09 |
| CT-027 | CE-26 | Bruno cancela reserva de Ana | 403; reserva e vínculo mantidos | F – DEF-08 |
| CT-028 | CE-28 | `GET /delete/<rid>` | 405; reserva mantida | F – DEF-10 |
| CT-029 | CE-21,23,25,27,30 | cancelar reserva com pagamento | reserva e pagamento removidos | F – DEF-11 |
| CT-030 | CE-31, CE-33 | `/rooms` sem filtro, com 101 reservado | lista 101, 102, 103 | P |
| CT-031 | CE-32 | visitante sem login: `/available` (GET/POST) e `/rooms` | redireciona a `/` | F – DEF-07 |
| CT-032 | CE-31,34,35,37,39,40,41,46 | 101 ocupado D+10–12; consulta D+10–12, 2 hóspedes | lista 102, 103 | P |
| CT-033 | CE-39 | 101 reservado em D+20; consulta D+10–12 | lista 101, 102, 103 | F – DEF-01 |
| CT-034 | CE-39 | 101 ocupado D+10–12; consulta D+12–14 | lista 101, 102, 103 | F – DEF-01 |
| CT-035 | CE-39 | idem; consulta D+8–10 | lista 101, 102, 103 | F – DEF-01 |
| CT-036 | CE-40 | idem; consulta D+11–13 | lista 102, 103 | P |
| CT-037 | CE-36 | consulta com entrada D+12 e saída D+10 | recusa (`/available`) | F – DEF-12 |
| CT-038 | CE-36 | consulta com entrada = saída | recusa | F – DEF-12 |
| CT-039 | CE-38 | consulta com 0 hóspedes | recusa | F – DEF-13 |
| CT-040 | CE-41 | consulta com 2 hóspedes | lista 101, 102, 103 | P |
| CT-041 | CE-42 | consulta com 3 hóspedes | lista 102, 103 | F – DEF-14 |
| CT-042 | CE-37, CE-41 | consulta com 1 hóspede | lista 101, 102, 103 | P |
| CT-043 | CE-35 | consulta de 1 noite | aceita; lista todos | P |
| CT-051 | CE-44 | reserva com entrada `2026-13-01` | recusa | F – DEF-18 |
| CT-052 | CE-45 | reserva com hóspedes `dois` | recusa | F – DEF-19 |
| CT-053 | CE-47 | consulta com entrada `amanhã` | recusa; lista sem filtro | F – DEF-18 |
| CT-054 | CE-48 | consulta com hóspedes `dois` | recusa | F – DEF-13 |
| CT-060 | CE-08, CE-20 | 101,102; 4 hóspedes (um abaixo da capacidade 5); 1 noite | aceita; custo 250 | P |
| CT-061 | CE-17 | 101 reservado D+10–12; nova D+7–9 | aceita | F – DEF-01 |
| CT-062 | CE-17 | idem; nova D+13–15 | aceita | F – DEF-01 |
| CT-063 | CE-39 | 101 ocupado D+10–12; consulta D+7–9 | lista 101, 102, 103 | F – DEF-01 |
| CT-064 | CE-39 | idem; consulta D+13–15 | lista 101, 102, 103 | F – DEF-01 |
