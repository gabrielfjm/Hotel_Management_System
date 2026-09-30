"""Etapa 2 - teste estrutural (caixa-branca).

Casos acrescentados depois de medir, com coverage.py (--cov-branch), a
cobertura dos casos funcionais sobre hotel/views.py original. Meta: 100% dos
comandos e 100% dos desvios viáveis das funções do recorte (reserve, cal_cost,
delete_reservation, check_available, show_rooms). O comentário de cada caso
indica as linhas/desvios do código original que ele passou a cobrir.
"""

import pytest

from hotel import app
from hotel.models import Booked, Reservations
from conftest import availability, booking, listed_rooms, login, path, seed_reservation


estrutural = pytest.mark.estrutural


@estrutural
@pytest.mark.ce("CE-17", "CE-19")
def test_CT_044_reserva_existente_de_outro_quarto_nao_gera_conflito(client, baseline):
    # Original: desvio 208->205 (vínculo de outro quarto) e 205->204 (fim do laço interno).
    seed_reservation(baseline["bruno"], room_numbers=(102,), offset=10)
    login(client)
    assert path(booking(client, room_numbers="101", offset=10)) == "/rooms"
    assert Reservations.query.count() == 2


@estrutural
@pytest.mark.ce("CE-17")
@pytest.mark.defeito("DEF-15", "vínculo de quarto é comparado com reservas de outros quartos")
def test_CT_045_reserva_de_outro_quarto_no_periodo_nao_bloqueia_quarto_livre(client, baseline):
    # Laço triplo reservas x vínculos sem brid == rid: a reserva de Bruno (102, D+20)
    # é combinada com o vínculo do 101 (reserva de Ana, D+10) e gera falso conflito.
    seed_reservation(baseline["ana"], room_numbers=(101,), offset=10)
    seed_reservation(baseline["bruno"], room_numbers=(102,), offset=20)
    login(client)
    assert path(booking(client, room_numbers="101", offset=20)) == "/rooms"
    assert Reservations.query.count() == 3


@estrutural
@pytest.mark.ce("CE-33")
@pytest.mark.defeito("DEF-16", "filtro de disponibilidade é global e vaza entre sessões")
def test_CT_046_consulta_de_um_usuario_nao_altera_listagem_de_outro(client, baseline):
    # Variável de módulo global_avail (linhas 140, 150, 177): estado compartilhado.
    seed_reservation(baseline["ana"])
    login(client, "ana")
    other = app.test_client()
    login(other, "bruno")
    availability(client, offset=10, nights=2)
    assert listed_rooms(other) == [101, 102, 103]


@estrutural
@pytest.mark.ce("CE-40")
@pytest.mark.defeito("DEF-17", "remoção durante a iteração pula o quarto seguinte")
def test_CT_047_consulta_omite_dois_quartos_ocupados_consecutivos(client, baseline):
    # Linha 163: all_rooms.remove(each) dentro de "for each in all_rooms".
    seed_reservation(baseline["ana"], room_numbers=(101, 102), offset=10)
    login(client)
    availability(client, guests="1", offset=10, nights=2)
    assert listed_rooms(client) == [103]


@estrutural
@pytest.mark.ce("CE-02", "CE-22", "CE-32")
def test_CT_048_sessao_encerrada_redireciona_nas_rotas_do_recorte(client, baseline):
    # Original: ramos falsos de "if session['user_available']" (linhas 88-89, 166-167, 180-181, 242-243).
    rid = seed_reservation(baseline["ana"])
    with client.session_transaction() as session:
        session["user_available"] = False
    assert path(client.get("/reserve")) == "/"
    assert path(client.get("/available")) == "/"
    assert path(client.get("/rooms")) == "/"
    assert path(client.post(f"/delete/{rid}")) == "/rooms"
    assert Reservations.query.get(rid) is not None


@estrutural
@pytest.mark.ce("CE-31")
def test_CT_049_formulario_de_disponibilidade_abre_para_usuario_autenticado(client):
    # Original: desvio 175->179 e linha 179 (GET renderiza o formulário).
    login(client)
    response = client.get("/available")
    assert response.status_code == 200
    assert b"Check Availability" in response.data
    assert b'name="checkin_date"' in response.data


@estrutural
@pytest.mark.ce("CE-01")
def test_CT_050_formulario_de_reserva_abre_para_usuario_autenticado(client):
    # Original: desvio 189->241 e linha 241 (GET renderiza o formulário).
    login(client)
    response = client.get("/reserve")
    assert response.status_code == 200
    assert b'name="room_numbers"' in response.data
    assert Booked.query.count() == 0
