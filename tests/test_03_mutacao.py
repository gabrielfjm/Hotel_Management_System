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
@pytest.mark.ce("CE-21", "CE-23", "CE-25", "CE-27")
def test_CT_057_titular_com_identificador_alto_cancela_propria_reserva(client):
    # Mata delete_reservation, ReplaceComparisonOperator_NotEq_IsNot (ocorrência 1):
    # "ruid is not uid" só coincide com "!=" para inteiros pequenos (cache do CPython, -5 a 256).
    carla = User("Carla", "Souza", "carla", "senha123", "carla@example.test")
    carla.uid = 1000
    db.session.add(carla)
    db.session.commit()
    rid = seed_reservation(1000)
    login(client, "carla")
    assert path(client.post(f"/delete/{rid}")) == "/rooms"
    assert Reservations.query.get(rid) is None


@mutacao
@pytest.mark.ce("CE-26")
def test_CT_058_usuario_de_id_menor_nao_cancela_reserva_de_id_maior(client, baseline):
    # Mata delete_reservation, ReplaceComparisonOperator_NotEq_Lt (ocorrência 1): "ruid < uid".
    # CT-027 só cobre o sentido inverso (Bruno, uid maior, tentando cancelar reserva de Ana).
    rid = seed_reservation(baseline["bruno"])
    login(client, "ana")
    assert client.post(f"/delete/{rid}").status_code == 403
    assert Reservations.query.get(rid) is not None


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
