"""Testes complementares de requisito secundário: RF-08 Cancelar reserva.

O recorte principal do estudo são REQ-01 (reservar quartos), REQ-02 (data de
entrada) e REQ-03 (data de saída). Estes casos, criados na primeira versão do
recorte, continuam executáveis e revelaram DEF-08 a DEF-11, mas ficam fora das
métricas das etapas (cobertura e mutação medem só as funções dos três
requisitos principais). Selecionar com: pytest -m secundario
"""

import pytest

from hotel.models import Booked, Payment, Reservations, Rooms, User, db
from conftest import login, path, seed_payment, seed_reservation


secundario = pytest.mark.secundario


@secundario
@pytest.mark.ce("CE-21", "CE-23", "CE-25", "CE-27", "CE-29")
def test_CT_024_titular_cancela_propria_reserva(client, baseline):
    rid = seed_reservation(baseline["ana"])
    login(client)
    response = client.post(f"/delete/{rid}")
    assert path(response) == "/rooms"
    assert Reservations.query.count() == 0
    assert Booked.query.count() == 0


@secundario
@pytest.mark.ce("CE-22")
@pytest.mark.defeito("DEF-07", "rota protegida sem sessão gera erro interno")
def test_CT_025_cancelamento_sem_sessao_redireciona_e_preserva(client, baseline):
    rid = seed_reservation(baseline["ana"])
    # O sistema envia o visitante à lista de quartos, que por sua vez exige login.
    assert path(client.post(f"/delete/{rid}")) == "/rooms"
    assert path(client.get("/rooms")) == "/"
    assert Reservations.query.get(rid) is not None


@secundario
@pytest.mark.ce("CE-24")
@pytest.mark.defeito("DEF-09", "cancelamento de reserva inexistente gera erro interno")
def test_CT_026_cancelamento_de_reserva_inexistente_retorna_404(client):
    login(client)
    assert client.post("/delete/999").status_code == 404


@secundario
@pytest.mark.ce("CE-26")
@pytest.mark.defeito("DEF-08", "usuário cancela reserva de outro usuário")
def test_CT_027_cancelamento_de_reserva_alheia_e_negado(client, baseline):
    rid = seed_reservation(baseline["ana"])
    login(client, "bruno")
    assert client.post(f"/delete/{rid}").status_code == 403
    assert Reservations.query.get(rid) is not None
    assert Booked.query.filter_by(brid=rid).count() == 1


@secundario
@pytest.mark.ce("CE-28")
@pytest.mark.defeito("DEF-10", "requisição GET exclui a reserva")
def test_CT_028_get_de_cancelamento_nao_altera_dados(client, baseline):
    rid = seed_reservation(baseline["ana"])
    login(client)
    assert client.get(f"/delete/{rid}").status_code == 405
    assert Reservations.query.get(rid) is not None


@secundario
@pytest.mark.ce("CE-21", "CE-23", "CE-25", "CE-27", "CE-30")
@pytest.mark.defeito("DEF-11", "pagamento fica órfão após o cancelamento")
def test_CT_029_cancelamento_com_pagamento_nao_deixa_registro_orfao(client, baseline):
    rid = seed_reservation(baseline["ana"])
    seed_payment(baseline["ana"], rid)
    login(client)
    assert path(client.post(f"/delete/{rid}")) == "/rooms"
    assert Reservations.query.count() == 0
    assert Payment.query.filter_by(prid=rid).count() == 0


@secundario
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


@secundario
@pytest.mark.ce("CE-26")
@pytest.mark.defeito("DEF-08", "usuário cancela reserva de outro usuário")
def test_CT_058_usuario_de_id_menor_nao_cancela_reserva_de_id_maior(client, baseline):
    # Mata delete_reservation, ReplaceComparisonOperator_NotEq_Lt (ocorrência 1): "ruid < uid".
    # CT-027 só cobre o sentido inverso (Bruno, uid maior, tentando cancelar reserva de Ana).
    rid = seed_reservation(baseline["bruno"])
    login(client, "ana")
    assert client.post(f"/delete/{rid}").status_code == 403
    assert Reservations.query.get(rid) is not None
