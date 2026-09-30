Legenda como na seção 4.3. Casos da marca `secundario` (fora das métricas).

| Caso | Classes | Entrada / cenário | Resultado esperado | Original |
|---|---|---|---|---|
| CT-024 | CE-21,23,25,27,29 | Ana cancela a própria reserva (`POST`) | `/rooms`; reserva e vínculo removidos | P |
| CT-025 | CE-22 | visitante sem login `POST /delete/<rid>` | redireciona; reserva mantida | F – DEF-07 |
| CT-026 | CE-24 | `POST /delete/999` | 404 | F – DEF-09 |
| CT-027 | CE-26 | Bruno cancela reserva de Ana | 403; reserva e vínculo mantidos | F – DEF-08 |
| CT-028 | CE-28 | `GET /delete/<rid>` | 405; reserva mantida | F – DEF-10 |
| CT-029 | CE-21,23,25,27,30 | cancelar reserva com pagamento | reserva e pagamento removidos | F – DEF-11 |
| CT-057 | CE-21, 23, 25, 27 | usuária com uid 1000 cancela a própria reserva (criado para um mutante de `delete_reservation`) | cancelada | P |
| CT-058 | CE-26 | Ana (uid 1) tenta cancelar reserva de Bruno (uid 2) | 403; reserva mantida | F – DEF-08 |
