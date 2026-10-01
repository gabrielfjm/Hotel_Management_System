"""Etapa 3 - teste baseado em defeitos (mutação com Cosmic Ray).

Casos acrescentados após a rodada inicial (evidencias/mutacao-inicial), cada
um para matar um mutante sobrevivente do código corrigido. O comentário
indica o mutante (linha, operador e ocorrência do Cosmic Ray).
"""

import pytest

from hotel.models import Booked, Reservations, Rooms, db
from conftest import booking, login, path, seed_reservation


mutacao = pytest.mark.mutacao


@mutacao
@pytest.mark.ce("CE-15", "CE-21")
def test_CT_020_saida_no_dia_da_entrada_de_outra_estadia_e_aceita(client, baseline):
    # Mata _periodos_conflitam, ReplaceComparisonOperator_Lt_LtE e Lt_IsNot (ocorrência 1):
    # "entrada_b <= saida_a" trataria estadias adjacentes como conflito. A etapa funcional só
    # testou o limite do outro lado (entrar no dia em que a outra estadia termina, CT-003).
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    assert path(booking(client, offset=8, nights=2)) == "/rooms"  # D+8 a D+10
    assert Reservations.query.count() == 2


@mutacao
@pytest.mark.ce("CE-15")
def test_CT_021_estadia_que_termina_antes_de_outra_comecar_e_aceita(client, baseline):
    # Mata _periodos_conflitam, ReplaceComparisonOperator_Lt_NotEq (ocorrência 1):
    # "entrada_b != saida_a" acusa conflito com qualquer estadia posterior não adjacente.
    seed_reservation(baseline["ana"], offset=10, nights=2)  # D+10 a D+12
    login(client)
    assert path(booking(client, offset=7, nights=2)) == "/rooms"  # D+7 a D+9
    assert Reservations.query.count() == 2


@mutacao
@pytest.mark.ce("CE-15")
def test_CT_022_vinculo_so_e_comparado_com_a_propria_reserva(client, baseline):
    # Mata _quartos_ocupados, ReplaceComparisonOperator_Eq_GtE: join Booked.brid >= Reservations.rid.
    # O vínculo do 101 (reserva 2, D+20) não pode herdar as datas da reserva 1 (quarto 102, D+10).
    seed_reservation(baseline["ana"], room_numbers=(102,), offset=10)
    seed_reservation(baseline["bruno"], room_numbers=(101,), offset=20)
    login(client)
    assert path(booking(client, room_numbers="101", offset=10)) == "/rooms"
    assert Reservations.query.count() == 3


@mutacao
@pytest.mark.ce("CE-05", "CE-10")
def test_CT_023_reserva_de_todos_os_quartos_do_hotel_e_aceita(client):
    # Mata _ler_quartos, ReplaceComparisonOperator_LtE_Lt: subconjunto próprio (<) em vez de <=.
    login(client)
    assert path(booking(client, room_numbers="101,102,103", guests="9", nights=2)) == "/rooms"
    assert Reservations.query.one().costs == (100 + 150 + 200) * 2
    assert sorted(b.room_id for b in Booked.query.all()) == [101, 102, 103]


@mutacao
@pytest.mark.ce("CE-22")
def test_CT_024_saida_anterior_a_entrada_e_rejeitada(client):
    # Mata reserve, ReplaceComparisonOperator_LtE_Eq (ocorrência 11): "d2 == d1" só recusa
    # 0 noites. A etapa funcional usou um único representante de CE-22 (saída = entrada).
    login(client)
    assert path(booking(client, nights=-1)) == "/reserve"
    assert Reservations.query.count() == 0


@mutacao
@pytest.mark.ce("CE-09", "CE-21")
def test_CT_025_custo_de_quarto_com_numero_acima_de_256(client):
    # Mata cal_cost, ReplaceComparisonOperator_Eq_Is: "is" só coincide com "==" para inteiros
    # pequenos; números de quarto como 301 são comuns em hotéis.
    room = Rooms(Rooms.query.get(101).room_type, 120, 2, "available")
    room.room_number = 301
    db.session.add(room)
    db.session.commit()
    login(client)
    assert path(booking(client, room_numbers="301", guests="2", nights=2)) == "/rooms"
    assert Reservations.query.one().costs == 240
