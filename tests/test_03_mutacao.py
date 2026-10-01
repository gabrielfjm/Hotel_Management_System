"""Etapa 3 - teste baseado em defeitos (mutação com Cosmic Ray) sobre os mesmos 15 casos.

A mutação foi aplicada aos 15 casos (já com as ampliações da etapa estrutural).
Nenhum caso novo é criado: os sobreviventes não equivalentes da rodada inicial
(evidencias/mutacao-inicial) foram mortos ampliando os casos que deveriam tê-los
detectado. Cada ampliação usa o identificador do caso que amplia; o comentário
indica o mutante (linha, operador e ocorrência do Cosmic Ray).
"""

import pytest

from hotel.models import Booked, Reservations
from conftest import login, path, reserva_existente, reservar


mutacao = pytest.mark.mutacao


@mutacao
@pytest.mark.ce("CE-05", "CE-10", "CE-11")
def test_CT_002_ampliacao_reserva_de_todos_os_quartos_do_hotel(client):
    # Mata _ler_quartos, ReplaceComparisonOperator_LtE_Lt: "set(numeros) < existentes" recusa
    # a reserva de TODOS os quartos. Mata também cal_cost, ReplaceComparisonOperator_Eq_Is:
    # "is" só coincide com "==" para inteiros pequenos (até 256); o quarto 301 revela a troca.
    login(client)
    assert path(reservar(client, quartos="101,102,301", hospedes=9, entrada="10/03/2030", saida="12/03/2030")) == "/rooms"
    assert Reservations.query.one().costs == (100 + 150 + 200) * 2
    assert sorted(b.room_id for b in Booked.query.all()) == [101, 102, 301]


@mutacao
@pytest.mark.ce("CE-15", "CE-21")
def test_CT_003_ampliacao_estadias_antes_da_reserva_existente(client, baseline):
    # Mata _periodos_conflitam, ReplaceComparisonOperator_Lt_LtE / Lt_IsNot / Lt_NotEq (ocorrência 1):
    # o caso só testava o lado "entrar no dia em que a outra sai"; faltava "sair no dia em que a
    # outra entra" (08 a 10/03) e uma estadia inteira antes da outra (05 a 07/03).
    reserva_existente(baseline["ana"], entrada="10/03/2030", saida="12/03/2030")
    login(client)
    assert path(reservar(client, entrada="08/03/2030", saida="10/03/2030")) == "/rooms"
    assert path(reservar(client, entrada="05/03/2030", saida="07/03/2030")) == "/rooms"
    assert Reservations.query.count() == 3


@mutacao
@pytest.mark.ce("CE-15")
def test_CT_012_ampliacao_ocupacao_de_outra_reserva_nao_e_herdada(client, baseline):
    # Mata _quartos_ocupados, ReplaceComparisonOperator_Eq_GtE: junção Booked.brid >= Reservations.rid.
    # O 101 (reserva 2, em 20/03) não pode herdar as datas da reserva 1 (quarto 102, em 10/03).
    reserva_existente(baseline["ana"], quartos=(102,), entrada="10/03/2030", saida="12/03/2030")
    reserva_existente(baseline["bruno"], quartos=(101,), entrada="20/03/2030", saida="22/03/2030")
    login(client)
    assert path(reservar(client, quartos="101", entrada="10/03/2030", saida="12/03/2030")) == "/rooms"
    assert Reservations.query.count() == 3


@mutacao
@pytest.mark.ce("CE-22")
def test_CT_015_ampliacao_saida_antes_da_entrada_e_recusada(client):
    # Mata reserve, ReplaceComparisonOperator_LtE_Eq (ocorrência 11): "d2 == d1" só recusa 0 noites.
    # O caso usava um único representante da classe CE-22 (saída igual à entrada).
    login(client)
    assert path(reservar(client, entrada="10/03/2030", saida="09/03/2030")) == "/reserve"
    assert Reservations.query.count() == 0
