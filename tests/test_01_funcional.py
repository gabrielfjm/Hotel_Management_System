"""Etapa 1 - teste funcional (caixa-preta).

Casos derivados da especificação (README do projeto e formulário de reserva)
por particionamento em classes de equivalência e análise do valor limite, sem
consultar o código. Recorte: REQ-01 Reservar quartos, REQ-02 Data de entrada e
REQ-03 Data de saída; o catálogo de classes está em tests/classes_equivalencia.json.

Regra de derivação: um caso válido cobre o maior número possível de classes
válidas (CT-001); cada classe inválida tem um caso próprio, com todas as outras
entradas válidas. Os limites (hóspedes, data de entrada, duração e estadias
adjacentes) reaproveitam esses casos sempre que possível.

Base de todos os casos (fixture ``baseline``): quartos 101 (R$ 100/noite,
2 pessoas), 102 (R$ 150, 3 pessoas) e 103 (R$ 200, 4 pessoas); usuários Ana e
Bruno. Datas são relativas ao dia da execução. Nos cenários com reserva
prévia, Ana ocupa o quarto 101 de D+10 a D+12 (saída exclusiva).
"""

import pytest

from hotel.models import Booked, Reservations
from conftest import booking, login, path, seed_reservation


funcional = pytest.mark.funcional


# ------------------------------------------------------------ casos válidos

@funcional
@pytest.mark.ce("CE-01", "CE-03", "CE-05", "CE-07", "CE-09", "CE-11", "CE-15", "CE-17", "CE-19", "CE-21")
def test_CT_001_reserva_valida_de_um_quarto_para_um_hospede(client):
    login(client)
    response = booking(client, room_numbers="101", guests="1", offset=10, nights=2)
    assert path(response) == "/rooms"
    reservation = Reservations.query.one()
    assert reservation.num_guests == 1
    assert reservation.costs == 200  # 2 noites x R$ 100
    assert [(b.brid, b.room_id) for b in Booked.query.all()] == [(reservation.rid, 101)]


@funcional
@pytest.mark.ce("CE-10", "CE-11")
def test_CT_002_varios_quartos_com_hospedes_no_limite_da_capacidade_somada(client):
    login(client)
    response = booking(client, room_numbers="101,102", guests="5", nights=3)
    assert path(response) == "/rooms"
    assert Reservations.query.one().costs == (100 + 150) * 3
    assert sorted(b.room_id for b in Booked.query.all()) == [101, 102]


@funcional
@pytest.mark.ce("CE-15", "CE-17")
@pytest.mark.defeito("DEF-01", "períodos sem interseção são tratados como conflito")
def test_CT_003_entrada_no_dia_da_saida_de_outra_estadia_e_aceita(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    assert path(booking(client, offset=12, nights=2)) == "/rooms"  # D+12 a D+14
    assert Reservations.query.count() == 2


@funcional
@pytest.mark.ce("CE-17", "CE-21")
@pytest.mark.defeito("DEF-02", "entrada no dia atual é rejeitada")
def test_CT_004_entrada_hoje_por_uma_noite_e_aceita(client):
    login(client)
    assert path(booking(client, offset=0, nights=1)) == "/rooms"
    assert Reservations.query.one().costs == 100


# ----------------------------------------------------------- casos inválidos

@funcional
@pytest.mark.ce("CE-02")
@pytest.mark.defeito("DEF-07", "rota protegida sem sessão gera erro interno")
def test_CT_005_reserva_sem_sessao_redireciona_para_inicio(client):
    assert path(client.get("/reserve")) == "/"
    assert path(booking(client)) == "/"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-04")
@pytest.mark.defeito("DEF-04", "número de quarto não numérico gera erro interno")
def test_CT_006_numero_de_quarto_nao_numerico_e_rejeitado(client):
    login(client)
    assert path(booking(client, room_numbers="abc")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-06")
@pytest.mark.defeito("DEF-05", "quarto inexistente é aceito junto com um quarto válido")
def test_CT_007_quarto_inexistente_e_rejeitado(client):
    login(client)
    assert path(booking(client, room_numbers="101,999", guests="2")) == "/reserve"
    assert Reservations.query.count() == 0
    assert Booked.query.count() == 0


@funcional
@pytest.mark.ce("CE-08")
@pytest.mark.defeito("DEF-06", "quarto repetido gera dois vínculos e custo em dobro")
def test_CT_008_quarto_repetido_e_rejeitado(client):
    login(client)
    assert path(booking(client, room_numbers="101,101", guests="2")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-12")
@pytest.mark.defeito("DEF-03", "reserva com zero hóspedes é gravada")
def test_CT_009_zero_hospedes_e_rejeitado(client):
    login(client)
    assert path(booking(client, guests="0")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-13")
def test_CT_010_hospedes_acima_da_capacidade_somada_sao_rejeitados(client):
    login(client)
    assert path(booking(client, room_numbers="101,102", guests="6")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-14")
@pytest.mark.defeito("DEF-19", "número de hóspedes não inteiro gera erro interno")
def test_CT_011_hospedes_nao_numerico_e_rejeitado(client):
    login(client)
    assert path(booking(client, guests="dois")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-16")
def test_CT_012_sobreposicao_de_uma_noite_e_rejeitada(client, baseline):
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    assert path(booking(client, offset=11, nights=2)) == "/reserve"  # D+11 a D+13
    assert Reservations.query.count() == 1


@funcional
@pytest.mark.ce("CE-18")
def test_CT_013_entrada_ontem_e_rejeitada(client):
    login(client)
    assert path(booking(client, offset=-1, nights=2)) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-20")
@pytest.mark.defeito("DEF-18", "data fora do formato MM/DD/AAAA gera erro interno")
def test_CT_014_data_de_entrada_malformada_e_rejeitada(client):
    login(client)
    response = client.post("/reserve", data={"checkin_date": "2026-13-01", "checkout_date": "01/20/2099",
                                              "num_guests": "2", "room_numbers": "101"})
    assert path(response) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-22")
def test_CT_015_saida_igual_a_entrada_e_rejeitada(client):
    login(client)
    assert path(booking(client, nights=0)) == "/reserve"
    assert Reservations.query.count() == 0
