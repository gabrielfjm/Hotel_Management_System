"""Etapa 3 - teste baseado em defeitos (mutação com Cosmic Ray).

Casos acrescentados após a rodada inicial (evidencias/mutacao-inicial), cada
um para matar um mutante sobrevivente do código corrigido. O comentário
indica o mutante (linha, operador e ocorrência do Cosmic Ray).
"""

import pytest

from hotel.models import Booked, Reservations, Rooms, User, db
from conftest import booking, login, path, seed_reservation


mutacao = pytest.mark.mutacao


@mutacao
@pytest.mark.ce("CE-17")
@pytest.mark.defeito("DEF-01", "períodos sem interseção são tratados como conflito")
def test_CT_055_vinculo_so_e_comparado_com_a_propria_reserva(client, baseline):
    # Mata _quartos_ocupados, ReplaceComparisonOperator_Eq_GtE: join Booked.brid >= Reservations.rid.
    # O vínculo do 101 (reserva 2, D+20) não pode herdar as datas da reserva 1 (quarto 102, D+10).
    seed_reservation(baseline["ana"], room_numbers=(102,), offset=10)
    seed_reservation(baseline["bruno"], room_numbers=(101,), offset=20)
    login(client)
    assert path(booking(client, room_numbers="101", offset=10)) == "/rooms"
    assert Reservations.query.count() == 3


@mutacao
@pytest.mark.ce("CE-13", "CE-20")
def test_CT_056_reserva_de_todos_os_quartos_do_hotel_e_aceita(client):
    # Mata _ler_quartos, ReplaceComparisonOperator_LtE_Lt: subconjunto próprio (<) em vez de <=.
    login(client)
    assert path(booking(client, room_numbers="101,102,103", guests="9", nights=2)) == "/rooms"
    assert Reservations.query.one().costs == (100 + 150 + 200) * 2
    assert sorted(b.room_id for b in Booked.query.all()) == [101, 102, 103]


@mutacao
@pytest.mark.ce("CE-05", "CE-19")
def test_CT_059_custo_de_quarto_com_numero_acima_de_256(client):
    # Mata cal_cost, ReplaceComparisonOperator_Eq_Is: "is" só coincide com "==" para inteiros
    # pequenos; números de quarto como 301 são comuns em hotéis.
    room = Rooms(Rooms.query.get(101).room_type, 120, 2, "available")
    room.room_number = 301
    db.session.add(room)
    db.session.commit()
    login(client)
    assert path(booking(client, room_numbers="301", guests="2", nights=2)) == "/rooms"
    assert Reservations.query.one().costs == 240
