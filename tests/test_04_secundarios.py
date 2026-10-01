"""Testes complementares de requisitos secundários: RF-08 Cancelar reserva e
RF-04 Consultar disponibilidade.

O recorte principal do estudo são REQ-01 (reservar quartos), REQ-02 (data de
entrada) e REQ-03 (data de saída). Estes casos ficam fora das métricas das
etapas (cobertura e mutação medem só as funções dos três requisitos
principais), mas revelaram DEF-08 a DEF-11 (cancelamento) e DEF-12 a DEF-17
(consulta), corrigidos no fork. Selecionar com: pytest -m secundario
"""

import pytest

from hotel.models import Booked, Payment, Reservations, Rooms, User, db
from hotel import app
from conftest import consultar, listed_rooms, login, path, reserva_existente, seed_payment, seed_reservation


secundario = pytest.mark.secundario


# ------------------------------------------------------- RF-08 Cancelar reserva


@secundario
@pytest.mark.ce("CE-31", "CE-33", "CE-35", "CE-37", "CE-39")
def test_CT_101_titular_cancela_propria_reserva(client, baseline):
    rid = seed_reservation(baseline["ana"])
    login(client)
    response = client.post(f"/delete/{rid}")
    assert path(response) == "/rooms"
    assert Reservations.query.count() == 0
    assert Booked.query.count() == 0


@secundario
@pytest.mark.ce("CE-32")
@pytest.mark.defeito("DEF-07", "rota protegida sem sessão gera erro interno")
def test_CT_102_cancelamento_sem_sessao_redireciona_e_preserva(client, baseline):
    rid = seed_reservation(baseline["ana"])
    # O sistema envia o visitante à lista de quartos, que por sua vez exige login.
    assert path(client.post(f"/delete/{rid}")) == "/rooms"
    assert path(client.get("/rooms")) == "/"
    assert Reservations.query.get(rid) is not None


@secundario
@pytest.mark.ce("CE-34")
@pytest.mark.defeito("DEF-09", "cancelamento de reserva inexistente gera erro interno")
def test_CT_103_cancelamento_de_reserva_inexistente_retorna_404(client):
    login(client)
    assert client.post("/delete/999").status_code == 404


@secundario
@pytest.mark.ce("CE-36")
@pytest.mark.defeito("DEF-08", "usuário cancela reserva de outro usuário")
def test_CT_104_cancelamento_de_reserva_alheia_e_negado(client, baseline):
    rid = seed_reservation(baseline["ana"])
    login(client, "bruno")
    assert client.post(f"/delete/{rid}").status_code == 403
    assert Reservations.query.get(rid) is not None
    assert Booked.query.filter_by(brid=rid).count() == 1


@secundario
@pytest.mark.ce("CE-38")
@pytest.mark.defeito("DEF-10", "requisição GET exclui a reserva")
def test_CT_105_get_de_cancelamento_nao_altera_dados(client, baseline):
    rid = seed_reservation(baseline["ana"])
    login(client)
    assert client.get(f"/delete/{rid}").status_code == 405
    assert Reservations.query.get(rid) is not None


@secundario
@pytest.mark.ce("CE-31", "CE-33", "CE-35", "CE-37", "CE-40")
@pytest.mark.defeito("DEF-11", "pagamento fica órfão após o cancelamento")
def test_CT_106_cancelamento_com_pagamento_nao_deixa_registro_orfao(client, baseline):
    rid = seed_reservation(baseline["ana"])
    seed_payment(baseline["ana"], rid)
    login(client)
    assert path(client.post(f"/delete/{rid}")) == "/rooms"
    assert Reservations.query.count() == 0
    assert Payment.query.filter_by(prid=rid).count() == 0


@secundario
@pytest.mark.ce("CE-31", "CE-33", "CE-35", "CE-37")
def test_CT_107_titular_com_identificador_alto_cancela_propria_reserva(client):
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
@pytest.mark.ce("CE-36")
@pytest.mark.defeito("DEF-08", "usuário cancela reserva de outro usuário")
def test_CT_108_usuario_de_id_menor_nao_cancela_reserva_de_id_maior(client, baseline):
    # Mata delete_reservation, ReplaceComparisonOperator_NotEq_Lt (ocorrência 1): "ruid < uid".
    # CT-104 só cobre o sentido inverso (Bruno, uid maior, tentando cancelar reserva de Ana).
    rid = seed_reservation(baseline["bruno"])
    login(client, "ana")
    assert client.post(f"/delete/{rid}").status_code == 403
    assert Reservations.query.get(rid) is not None


# ------------------------------------------- RF-04 Consultar disponibilidade

@secundario
@pytest.mark.ce("CE-41", "CE-43", "CE-45", "CE-46")
def test_CT_111_consulta_omite_quarto_ocupado_e_lista_livres(client, baseline):
    reserva_existente(baseline["ana"], entrada="10/03/2030", saida="12/03/2030")
    login(client)
    assert path(consultar(client, hospedes=2, entrada="10/03/2030", saida="12/03/2030")) == "/rooms"
    assert listed_rooms(client) == [102, 301]


@secundario
@pytest.mark.ce("CE-42")
@pytest.mark.defeito("DEF-12", "consulta aceita período vazio ou invertido")
def test_CT_112_consulta_com_datas_invertidas_e_rejeitada(client):
    login(client)
    assert path(consultar(client, entrada="12/03/2030", saida="10/03/2030")) == "/available"


@secundario
@pytest.mark.ce("CE-44")
@pytest.mark.defeito("DEF-13", "consulta aceita zero hóspedes")
def test_CT_113_consulta_com_zero_hospedes_e_rejeitada(client):
    login(client)
    assert path(consultar(client, hospedes=0)) == "/available"


@secundario
@pytest.mark.ce("CE-46")
@pytest.mark.defeito("DEF-14", "consulta ignora a quantidade de hóspedes")
def test_CT_114_hospedes_acima_da_capacidade_ocultam_o_quarto(client):
    login(client)
    consultar(client, hospedes=3)
    assert listed_rooms(client) == [102, 301]


@secundario
@pytest.mark.ce("CE-47")
@pytest.mark.defeito("DEF-16", "filtro de disponibilidade é global e vaza entre sessões")
def test_CT_115_consulta_de_um_usuario_nao_altera_listagem_de_outro(client, baseline):
    # Variável de módulo global_avail: estado compartilhado entre sessões.
    reserva_existente(baseline["ana"], entrada="10/03/2030", saida="12/03/2030")
    login(client, "ana")
    other = app.test_client()
    login(other, "bruno")
    consultar(client, entrada="10/03/2030", saida="12/03/2030")
    assert listed_rooms(other) == [101, 102, 301]


@secundario
@pytest.mark.ce("CE-46")
@pytest.mark.defeito("DEF-17", "remoção durante a iteração pula o quarto seguinte")
def test_CT_116_consulta_omite_dois_quartos_ocupados_consecutivos(client, baseline):
    # all_rooms.remove(each) dentro de "for each in all_rooms".
    reserva_existente(baseline["ana"], quartos=(101, 102), entrada="10/03/2030", saida="12/03/2030")
    login(client)
    consultar(client, hospedes=1, entrada="10/03/2030", saida="12/03/2030")
    assert listed_rooms(client) == [301]
