"""Etapa 1 - teste funcional (caixa-preta).

Casos derivados da especificação (README do projeto e interface web) por
particionamento em classes de equivalência (CE-01 a CE-42) e análise do valor
limite, sem consultar o código. Cada classe inválida tem pelo menos um caso
que a exercita isoladamente; as demais entradas do caso pertencem a classes
válidas.

Base de todos os casos (fixture ``baseline``): quartos 101 (R$ 100/noite,
2 pessoas), 102 (R$ 150, 3 pessoas) e 103 (R$ 200, 4 pessoas); usuários Ana e
Bruno. Datas são relativas ao dia da execução. Nos cenários com reserva
prévia, Ana ocupa o quarto 101 de D+10 a D+12 (saída exclusiva).
"""

import pytest

from hotel.models import Booked, Payment, Reservations
from conftest import (availability, booking, listed_rooms, login, path, seed_payment,
                      seed_reservation)


funcional = pytest.mark.funcional


# ---------------------------------------------------------------- REQ-01 Reserva

@funcional
@pytest.mark.ce("CE-01", "CE-03", "CE-05", "CE-08", "CE-11", "CE-13", "CE-15", "CE-17", "CE-19")
def test_CT_001_reserva_valida_de_um_quarto_por_duas_noites(client):
    login(client)
    response = booking(client, room_numbers="101", guests="2", offset=10, nights=2)
    assert path(response) == "/rooms"
    reservation = Reservations.query.one()
    assert reservation.num_guests == 2
    assert reservation.costs == 200  # 2 noites x R$ 100
    assert [(b.brid, b.room_id) for b in Booked.query.all()] == [(reservation.rid, 101)]


@funcional
@pytest.mark.ce("CE-08", "CE-20")
def test_CT_002_varios_quartos_com_hospedes_no_limite_da_capacidade_somada(client):
    login(client)
    response = booking(client, room_numbers="101,102", guests="5", nights=3)
    assert path(response) == "/rooms"
    assert Reservations.query.one().costs == (100 + 150) * 3
    assert sorted(b.room_id for b in Booked.query.all()) == [101, 102]


@funcional
@pytest.mark.ce("CE-08")
def test_CT_003_hospedes_iguais_a_capacidade_do_quarto_sao_aceitos(client):
    login(client)
    assert path(booking(client, guests="2")) == "/rooms"
    assert Reservations.query.one().num_guests == 2


@funcional
@pytest.mark.ce("CE-10")
def test_CT_004_hospedes_acima_da_capacidade_do_quarto_sao_rejeitados(client):
    login(client)
    assert path(booking(client, guests="3")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-10")
def test_CT_005_hospedes_acima_da_capacidade_somada_sao_rejeitados(client):
    login(client)
    assert path(booking(client, room_numbers="101,102", guests="6")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-08")
def test_CT_006_um_hospede_limite_inferior_e_aceito(client):
    login(client)
    assert path(booking(client, guests="1")) == "/rooms"
    assert Reservations.query.one().num_guests == 1


@funcional
@pytest.mark.ce("CE-09")
@pytest.mark.defeito("DEF-03", "reserva com zero hóspedes é gravada")
def test_CT_007_zero_hospedes_e_rejeitado(client):
    login(client)
    assert path(booking(client, guests="0")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-05")
def test_CT_008_uma_noite_limite_inferior_custa_uma_diaria(client):
    login(client)
    assert path(booking(client, nights=1)) == "/rooms"
    assert Reservations.query.one().costs == 100


@funcional
@pytest.mark.ce("CE-06")
def test_CT_009_saida_igual_a_entrada_zero_noites_e_rejeitada(client):
    login(client)
    assert path(booking(client, nights=0)) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-07")
def test_CT_010_saida_anterior_a_entrada_e_rejeitada(client):
    login(client)
    assert path(booking(client, nights=-1)) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-03")
@pytest.mark.defeito("DEF-02", "entrada no dia atual é rejeitada")
def test_CT_011_entrada_hoje_limite_e_aceita(client):
    login(client)
    assert path(booking(client, offset=0, nights=1)) == "/rooms"
    assert Reservations.query.count() == 1


@funcional
@pytest.mark.ce("CE-03")
def test_CT_012_entrada_amanha_e_aceita(client):
    login(client)
    assert path(booking(client, offset=1, nights=1)) == "/rooms"
    assert Reservations.query.count() == 1


@funcional
@pytest.mark.ce("CE-04")
def test_CT_013_entrada_ontem_e_rejeitada(client):
    login(client)
    assert path(booking(client, offset=-1, nights=2)) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-02")
@pytest.mark.defeito("DEF-07", "rota protegida sem sessão gera erro interno")
def test_CT_014_reserva_sem_sessao_redireciona_para_inicio(client):
    assert path(client.get("/reserve")) == "/"
    assert path(booking(client)) == "/"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-12")
@pytest.mark.defeito("DEF-04", "número de quarto não numérico gera erro interno")
def test_CT_015_numero_de_quarto_nao_numerico_e_rejeitado(client):
    login(client)
    assert path(booking(client, room_numbers="abc")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-14")
@pytest.mark.defeito("DEF-05", "quarto inexistente é aceito junto com um quarto válido")
def test_CT_016_quarto_inexistente_e_rejeitado(client):
    login(client)
    assert path(booking(client, room_numbers="101,999", guests="2")) == "/reserve"
    assert Reservations.query.count() == 0
    assert Booked.query.count() == 0


@funcional
@pytest.mark.ce("CE-16")
@pytest.mark.defeito("DEF-06", "quarto repetido gera dois vínculos e custo em dobro")
def test_CT_017_quarto_repetido_e_rejeitado(client):
    login(client)
    assert path(booking(client, room_numbers="101,101", guests="2")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-18")
def test_CT_018_mesmo_quarto_no_mesmo_periodo_e_rejeitado(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)
    login(client)
    assert path(booking(client, offset=10, nights=2)) == "/reserve"
    assert Reservations.query.count() == 1


@funcional
@pytest.mark.ce("CE-18")
def test_CT_019_sobreposicao_de_uma_noite_no_inicio_e_rejeitada(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    assert path(booking(client, offset=9, nights=2)) == "/reserve"  # D+9 a D+11
    assert Reservations.query.count() == 1


@funcional
@pytest.mark.ce("CE-18")
def test_CT_020_sobreposicao_de_uma_noite_no_fim_e_rejeitada(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    assert path(booking(client, offset=11, nights=2)) == "/reserve"  # D+11 a D+13
    assert Reservations.query.count() == 1


@funcional
@pytest.mark.ce("CE-17")
@pytest.mark.defeito("DEF-01", "períodos sem interseção são tratados como conflito")
def test_CT_021_saida_no_dia_da_entrada_existente_e_aceita(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    assert path(booking(client, offset=8, nights=2)) == "/rooms"  # D+8 a D+10
    assert Reservations.query.count() == 2


@funcional
@pytest.mark.ce("CE-17")
@pytest.mark.defeito("DEF-01", "períodos sem interseção são tratados como conflito")
def test_CT_022_entrada_no_dia_da_saida_existente_e_aceita(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    assert path(booking(client, offset=12, nights=2)) == "/rooms"  # D+12 a D+14
    assert Reservations.query.count() == 2


@funcional
@pytest.mark.ce("CE-17")
@pytest.mark.defeito("DEF-01", "períodos sem interseção são tratados como conflito")
def test_CT_023_mesmo_quarto_em_periodo_distante_e_aceito(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)
    login(client)
    assert path(booking(client, offset=20, nights=2)) == "/rooms"
    assert Reservations.query.count() == 2


# ----------------------------------------------------------- REQ-02 Cancelamento

@funcional
@pytest.mark.ce("CE-21", "CE-23", "CE-25", "CE-27", "CE-29")
def test_CT_024_titular_cancela_propria_reserva(client, baseline):
    rid = seed_reservation(baseline["ana"])
    login(client)
    response = client.post(f"/delete/{rid}")
    assert path(response) == "/rooms"
    assert Reservations.query.count() == 0
    assert Booked.query.count() == 0


@funcional
@pytest.mark.ce("CE-22")
@pytest.mark.defeito("DEF-07", "rota protegida sem sessão gera erro interno")
def test_CT_025_cancelamento_sem_sessao_redireciona_e_preserva(client, baseline):
    rid = seed_reservation(baseline["ana"])
    # O sistema envia o visitante à lista de quartos, que por sua vez exige login.
    assert path(client.post(f"/delete/{rid}")) == "/rooms"
    assert path(client.get("/rooms")) == "/"
    assert Reservations.query.get(rid) is not None


@funcional
@pytest.mark.ce("CE-24")
@pytest.mark.defeito("DEF-09", "cancelamento de reserva inexistente gera erro interno")
def test_CT_026_cancelamento_de_reserva_inexistente_retorna_404(client):
    login(client)
    assert client.post("/delete/999").status_code == 404


@funcional
@pytest.mark.ce("CE-26")
@pytest.mark.defeito("DEF-08", "usuário cancela reserva de outro usuário")
def test_CT_027_cancelamento_de_reserva_alheia_e_negado(client, baseline):
    rid = seed_reservation(baseline["ana"])
    login(client, "bruno")
    assert client.post(f"/delete/{rid}").status_code == 403
    assert Reservations.query.get(rid) is not None
    assert Booked.query.filter_by(brid=rid).count() == 1


@funcional
@pytest.mark.ce("CE-28")
@pytest.mark.defeito("DEF-10", "requisição GET exclui a reserva")
def test_CT_028_get_de_cancelamento_nao_altera_dados(client, baseline):
    rid = seed_reservation(baseline["ana"])
    login(client)
    assert client.get(f"/delete/{rid}").status_code == 405
    assert Reservations.query.get(rid) is not None


@funcional
@pytest.mark.ce("CE-21", "CE-23", "CE-25", "CE-27", "CE-30")
@pytest.mark.defeito("DEF-11", "pagamento fica órfão após o cancelamento")
def test_CT_029_cancelamento_com_pagamento_nao_deixa_registro_orfao(client, baseline):
    rid = seed_reservation(baseline["ana"])
    seed_payment(baseline["ana"], rid)
    login(client)
    assert path(client.post(f"/delete/{rid}")) == "/rooms"
    assert Reservations.query.count() == 0
    assert Payment.query.filter_by(prid=rid).count() == 0


# ------------------------------------------------------ REQ-03 Disponibilidade

@funcional
@pytest.mark.ce("CE-31", "CE-33")
def test_CT_030_consulta_sem_filtro_lista_todos_os_quartos(client, baseline):
    seed_reservation(baseline["ana"])
    login(client)
    assert listed_rooms(client) == [101, 102, 103]


@funcional
@pytest.mark.ce("CE-32")
@pytest.mark.defeito("DEF-07", "rota protegida sem sessão gera erro interno")
def test_CT_031_consulta_sem_sessao_redireciona_para_inicio(client):
    assert path(client.get("/available")) == "/"
    assert path(availability(client)) == "/"
    assert path(client.get("/rooms")) == "/"


@funcional
@pytest.mark.ce("CE-31", "CE-34", "CE-35", "CE-37", "CE-39", "CE-40", "CE-41")
def test_CT_032_consulta_omite_quarto_ocupado_e_lista_livres(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)
    login(client)
    assert path(availability(client, guests="2", offset=10, nights=2)) == "/rooms"
    assert listed_rooms(client) == [102, 103]


@funcional
@pytest.mark.ce("CE-39")
@pytest.mark.defeito("DEF-01", "períodos sem interseção são tratados como conflito")
def test_CT_033_reserva_em_periodo_distante_nao_oculta_quarto(client, baseline):
    seed_reservation(baseline["ana"], offset=20, nights=2)
    login(client)
    availability(client, offset=10, nights=2)
    assert listed_rooms(client) == [101, 102, 103]


@funcional
@pytest.mark.ce("CE-39")
@pytest.mark.defeito("DEF-01", "períodos sem interseção são tratados como conflito")
def test_CT_034_entrada_da_consulta_no_dia_da_saida_existente_exibe_quarto(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    availability(client, offset=12, nights=2)  # D+12 a D+14
    assert listed_rooms(client) == [101, 102, 103]


@funcional
@pytest.mark.ce("CE-39")
@pytest.mark.defeito("DEF-01", "períodos sem interseção são tratados como conflito")
def test_CT_035_saida_da_consulta_no_dia_da_entrada_existente_exibe_quarto(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    availability(client, offset=8, nights=2)  # D+8 a D+10
    assert listed_rooms(client) == [101, 102, 103]


@funcional
@pytest.mark.ce("CE-40")
def test_CT_036_consulta_com_sobreposicao_de_uma_noite_omite_quarto(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    availability(client, offset=11, nights=2)  # D+11 a D+13
    assert listed_rooms(client) == [102, 103]


@funcional
@pytest.mark.ce("CE-36")
@pytest.mark.defeito("DEF-12", "consulta aceita período vazio ou invertido")
def test_CT_037_consulta_com_datas_invertidas_e_rejeitada(client):
    login(client)
    assert path(availability(client, offset=12, nights=-2)) == "/available"


@funcional
@pytest.mark.ce("CE-36")
@pytest.mark.defeito("DEF-12", "consulta aceita período vazio ou invertido")
def test_CT_038_consulta_com_entrada_igual_a_saida_e_rejeitada(client):
    login(client)
    assert path(availability(client, offset=10, nights=0)) == "/available"


@funcional
@pytest.mark.ce("CE-38")
@pytest.mark.defeito("DEF-13", "consulta aceita zero hóspedes")
def test_CT_039_consulta_com_zero_hospedes_e_rejeitada(client):
    login(client)
    assert path(availability(client, guests="0")) == "/available"


@funcional
@pytest.mark.ce("CE-41")
def test_CT_040_hospedes_iguais_a_capacidade_exibem_o_quarto(client):
    login(client)
    availability(client, guests="2")
    assert listed_rooms(client) == [101, 102, 103]


@funcional
@pytest.mark.ce("CE-42")
@pytest.mark.defeito("DEF-14", "consulta ignora a quantidade de hóspedes")
def test_CT_041_hospedes_acima_da_capacidade_ocultam_o_quarto(client):
    login(client)
    availability(client, guests="3")
    assert listed_rooms(client) == [102, 103]


@funcional
@pytest.mark.ce("CE-37", "CE-41")
def test_CT_042_um_hospede_limite_inferior_lista_quartos_livres(client):
    login(client)
    assert path(availability(client, guests="1")) == "/rooms"
    assert listed_rooms(client) == [101, 102, 103]


@funcional
@pytest.mark.ce("CE-35")
def test_CT_043_consulta_de_uma_noite_limite_inferior_e_aceita(client):
    login(client)
    assert path(availability(client, nights=1)) == "/rooms"
    assert listed_rooms(client) == [101, 102, 103]


# ------------------------------------------- Revisão da tabela de classes
# Condições de entrada acrescentadas ao revisar a especificação do formulário
# (datas no formato MM/DD/AAAA e número de hóspedes inteiro): CE-43 a CE-48.

@funcional
@pytest.mark.ce("CE-44")
@pytest.mark.defeito("DEF-18", "data fora do formato MM/DD/AAAA gera erro interno")
def test_CT_051_reserva_com_data_malformada_e_rejeitada(client):
    login(client)
    response = client.post("/reserve", data={"checkin_date": "2026-13-01", "checkout_date": "01/20/2099",
                                              "num_guests": "2", "room_numbers": "101"})
    assert path(response) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-45")
@pytest.mark.defeito("DEF-19", "número de hóspedes não inteiro gera erro interno")
def test_CT_052_reserva_com_hospedes_nao_numerico_e_rejeitada(client):
    login(client)
    assert path(booking(client, guests="dois")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-47")
@pytest.mark.defeito("DEF-18", "data fora do formato MM/DD/AAAA gera erro interno")
def test_CT_053_consulta_com_data_malformada_e_rejeitada(client):
    login(client)
    response = client.post("/available", data={"checkin_date": "amanhã", "checkout_date": "01/20/2099",
                                                "num_guests": "2"})
    assert path(response) == "/available"
    assert listed_rooms(client) == [101, 102, 103]


@funcional
@pytest.mark.ce("CE-48")
@pytest.mark.defeito("DEF-13", "consulta aceita quantidade de hóspedes inválida")
def test_CT_054_consulta_com_hospedes_nao_numerico_e_rejeitada(client):
    login(client)
    assert path(availability(client, guests="dois")) == "/available"
