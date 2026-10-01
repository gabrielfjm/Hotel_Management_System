"""Etapa 1 - teste funcional (caixa-preta): os 15 casos de teste do estudo.

Casos derivados da especificação (README do projeto e formulário de reserva)
por particionamento em classes de equivalência e análise do valor limite, sem
consultar o código. Recorte: REQ-01 Reservar quartos, REQ-02 Data de entrada e
REQ-03 Data de saída; o catálogo de classes está em tests/classes_equivalencia.json.

Os mesmos 15 casos são reaproveitados nas etapas seguintes: a etapa estrutural
(test_02_estrutural.py) e a de mutação (test_03_mutacao.py) não criam casos
novos, apenas ampliam alguns deles com o cenário que faltava. As ampliações
usam o mesmo identificador (CT-xxx) do caso que ampliam.

Regra de derivação: um caso válido cobre o maior número possível de classes
válidas (CT-001); cada classe inválida tem um caso próprio, com todas as outras
entradas válidas. Os limites (hóspedes, data de entrada, duração e estadias
encostadas) ficam embutidos nesses casos.

Base de todos os casos (fixture ``baseline``): quartos 101 (R$ 100/noite,
2 pessoas), 102 (R$ 150, 3 pessoas) e 301 (R$ 200, 4 pessoas); usuários Ana e
Bruno. As datas são reais (março de 2030), exceto nos casos de "hoje" e "ontem",
que dependem do dia da execução. Nos cenários com reserva prévia, o quarto 101
está ocupado de 10/03/2030 a 12/03/2030 (a noite da saída não conta).
"""

import pytest

from hotel.models import Booked, Reservations
from conftest import hoje, login, path, reserva_existente, reservar


funcional = pytest.mark.funcional


# ------------------------------------------------------------ casos válidos

@funcional
@pytest.mark.ce("CE-01", "CE-03", "CE-05", "CE-07", "CE-09", "CE-11", "CE-15", "CE-17", "CE-19", "CE-21")
def test_CT_001_reserva_simples_de_um_quarto_e_aceita(client):
    login(client)
    resposta = reservar(client, quartos="101", hospedes=1, entrada="10/03/2030", saida="12/03/2030")
    assert path(resposta) == "/rooms"
    reserva = Reservations.query.one()
    assert reserva.num_guests == 1
    assert reserva.costs == 200  # 2 noites x R$ 100
    assert [(b.brid, b.room_id) for b in Booked.query.all()] == [(reserva.rid, 101)]


@funcional
@pytest.mark.ce("CE-10", "CE-11")
def test_CT_002_reserva_de_dois_quartos_com_lotacao_maxima_e_aceita(client):
    login(client)
    resposta = reservar(client, quartos="101,102", hospedes=5, entrada="10/03/2030", saida="13/03/2030")
    assert path(resposta) == "/rooms"
    assert Reservations.query.one().costs == (100 + 150) * 3
    assert sorted(b.room_id for b in Booked.query.all()) == [101, 102]


@funcional
@pytest.mark.ce("CE-15", "CE-17")
@pytest.mark.defeito("DEF-01", "períodos sem interseção são tratados como conflito")
def test_CT_003_estadia_que_comeca_quando_outra_termina_e_aceita(client, baseline):
    reserva_existente(baseline["ana"], entrada="10/03/2030", saida="12/03/2030")
    login(client)
    assert path(reservar(client, entrada="12/03/2030", saida="14/03/2030")) == "/rooms"
    assert Reservations.query.count() == 2


@funcional
@pytest.mark.ce("CE-17", "CE-21")
@pytest.mark.defeito("DEF-02", "entrada no dia atual é rejeitada")
def test_CT_004_entrada_hoje_e_aceita(client):
    login(client)
    assert path(reservar(client, entrada=hoje(), saida=hoje(1))) == "/rooms"
    assert Reservations.query.one().costs == 100  # 1 diária


# ----------------------------------------------------------- casos inválidos

@funcional
@pytest.mark.ce("CE-02")
@pytest.mark.defeito("DEF-07", "rota protegida sem sessão gera erro interno")
def test_CT_005_visitante_sem_login_nao_reserva(client):
    assert path(client.get("/reserve")) == "/"
    assert path(reservar(client)) == "/"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-04")
@pytest.mark.defeito("DEF-04", "número de quarto não numérico gera erro interno")
def test_CT_006_quarto_escrito_em_texto_e_recusado(client):
    login(client)
    assert path(reservar(client, quartos="abc")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-06")
@pytest.mark.defeito("DEF-05", "quarto inexistente é aceito junto com um quarto válido")
def test_CT_007_quarto_que_nao_existe_e_recusado(client):
    login(client)
    assert path(reservar(client, quartos="101,999", hospedes=2)) == "/reserve"
    assert Reservations.query.count() == 0
    assert Booked.query.count() == 0


@funcional
@pytest.mark.ce("CE-08")
@pytest.mark.defeito("DEF-06", "quarto repetido gera dois vínculos e custo em dobro")
def test_CT_008_quarto_repetido_e_recusado(client):
    login(client)
    assert path(reservar(client, quartos="101,101", hospedes=2)) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-12")
@pytest.mark.defeito("DEF-03", "reserva com zero hóspedes é gravada")
def test_CT_009_reserva_sem_hospedes_e_recusada(client):
    login(client)
    assert path(reservar(client, hospedes=0)) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-13")
def test_CT_010_hospedes_acima_da_capacidade_sao_recusados(client):
    login(client)
    assert path(reservar(client, quartos="101,102", hospedes=6)) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-14")
@pytest.mark.defeito("DEF-19", "número de hóspedes não inteiro gera erro interno")
def test_CT_011_hospedes_escritos_por_extenso_sao_recusados(client):
    login(client)
    assert path(reservar(client, hospedes="dois")) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-16")
def test_CT_012_quarto_ocupado_no_periodo_e_recusado(client, baseline):
    reserva_existente(baseline["ana"], entrada="10/03/2030", saida="12/03/2030")
    login(client)
    assert path(reservar(client, entrada="11/03/2030", saida="13/03/2030")) == "/reserve"  # noite de 11/03 em comum
    assert Reservations.query.count() == 1


@funcional
@pytest.mark.ce("CE-18")
def test_CT_013_entrada_no_passado_e_recusada(client):
    login(client)
    assert path(reservar(client, entrada=hoje(-1), saida=hoje(1))) == "/reserve"  # entrada ontem
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-20")
@pytest.mark.defeito("DEF-18", "data fora do formato MM/DD/AAAA gera erro interno")
def test_CT_014_data_em_formato_errado_e_recusada(client):
    login(client)
    resposta = client.post("/reserve", data={"checkin_date": "2030-13-01", "checkout_date": "03/12/2030",
                                              "num_guests": "2", "room_numbers": "101"})
    assert path(resposta) == "/reserve"
    assert Reservations.query.count() == 0


@funcional
@pytest.mark.ce("CE-22")
def test_CT_015_saida_igual_a_entrada_e_recusada(client):
    login(client)
    assert path(reservar(client, entrada="10/03/2030", saida="10/03/2030")) == "/reserve"  # 0 noites
    assert Reservations.query.count() == 0
