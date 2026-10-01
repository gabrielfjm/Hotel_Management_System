Legenda como na seção 4.3. Casos da marca `secundario` (fora das métricas).

| Caso | RF | Classes | Entrada / cenário | Resultado esperado | Original |
|---|---|---|---|---|---|
| CT-101 | RF-08 | CE-31, 33, 35, 37, 39 | Ana cancela a própria reserva (`POST`) | `/rooms`; reserva e vínculo removidos | P |
| CT-102 | RF-08 | CE-32 | visitante sem login `POST /delete/<rid>` | redireciona; reserva mantida | F – DEF-07 |
| CT-103 | RF-08 | CE-34 | `POST /delete/999` | 404 | F – DEF-09 |
| CT-104 | RF-08 | CE-36 | Bruno cancela reserva de Ana | 403; reserva e vínculo mantidos | F – DEF-08 |
| CT-105 | RF-08 | CE-38 | `GET /delete/<rid>` | 405; reserva mantida | F – DEF-10 |
| CT-106 | RF-08 | CE-31, 33, 35, 37, 40 | cancelar reserva com pagamento | reserva e pagamento removidos | F – DEF-11 |
| CT-107 | RF-08 | CE-31, 33, 35, 37 | usuária com uid 1000 cancela a própria reserva | cancelada | P |
| CT-108 | RF-08 | CE-36 | Ana (uid 1) tenta cancelar reserva de Bruno (uid 2) | 403; reserva mantida | F – DEF-08 |
| CT-111 | RF-04 | CE-41, 43, 45, 46 | 101 ocupado D+10–12; consulta D+10–12, 2 hóspedes | lista 102, 103 | P |
| CT-112 | RF-04 | CE-42 | consulta com entrada D+12 e saída D+10 | recusa (`/available`) | F – DEF-12 |
| CT-113 | RF-04 | CE-44 | consulta com 0 hóspedes | recusa | F – DEF-13 |
| CT-114 | RF-04 | CE-46 | consulta com 3 hóspedes | lista 102, 103 (o 101 comporta 2) | F – DEF-14 |
| CT-115 | RF-04 | CE-47 | Ana consulta D+10 com o 101 ocupado; Bruno, em outra sessão, abre `/rooms` | Bruno vê 101, 102, 103 | F – DEF-16 |
| CT-116 | RF-04 | CE-46 | 101 e 102 ocupados em D+10; consulta D+10, 1 hóspede | só o 103 | F – DEF-17 |
