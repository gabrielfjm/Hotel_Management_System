"""Etapa 2 - teste estrutural (caixa-branca).

Casos acrescentados depois de medir, com coverage.py (--cov-branch), a
cobertura dos casos funcionais sobre hotel/views.py original. Meta: 100% dos
comandos e 100% dos desvios viáveis das funções do recorte (reserve e
cal_cost). O comentário de cada caso indica as linhas/desvios do código
original que ele passou a cobrir.
"""

import pytest

from hotel.models import Booked, Reservations
from conftest import booking, login, path, seed_reservation


estrutural = pytest.mark.estrutural


@estrutural
@pytest.mark.ce("CE-01")
def test_CT_016_formulario_de_reserva_abre_para_usuario_autenticado(client):
    # Original: desvio 189->241 e linha 241 (GET renderiza o formulário).
    login(client)
    response = client.get("/reserve")
    assert response.status_code == 200
    assert b'name="room_numbers"' in response.data
    assert Booked.query.count() == 0


@estrutural
@pytest.mark.ce("CE-02")
def test_CT_017_sessao_encerrada_redireciona_para_inicio(client):
    # Original: desvio 186->242 e linhas 242-243 (ramo falso de "if session['user_available']").
    # Os casos funcionais sem login não criam a chave e o original lança KeyError antes do if;
    # o ramo falso só roda com a chave valendo False, estado deixado pelo logout.
    with client.session_transaction() as session:
        session["user_available"] = False
    assert path(client.get("/reserve")) == "/"
    assert path(booking(client)) == "/"
    assert Reservations.query.count() == 0


@estrutural
@pytest.mark.ce("CE-15", "CE-09")
def test_CT_018_reserva_existente_de_outro_quarto_nao_gera_conflito(client, baseline):
    # Original: desvio 208->205 (vínculo de outro quarto) e 205->204 (fim do laço interno).
    seed_reservation(baseline["bruno"], room_numbers=(102,), offset=10)
    login(client)
    assert path(booking(client, room_numbers="101", offset=10)) == "/rooms"
    assert Reservations.query.count() == 2


@estrutural
@pytest.mark.ce("CE-15")
@pytest.mark.defeito("DEF-15", "vínculo de quarto é comparado com reservas de outros quartos")
def test_CT_019_reserva_de_outro_quarto_no_periodo_nao_bloqueia_quarto_livre(client, baseline):
    # Laço triplo reservas x vínculos sem brid == rid (linhas 203-212): a reserva de Bruno
    # (102, D+20) é combinada com o vínculo do 101 (reserva de Ana, D+10) e gera falso conflito.
    seed_reservation(baseline["ana"], room_numbers=(101,), offset=10)
    seed_reservation(baseline["bruno"], room_numbers=(102,), offset=20)
    login(client)
    assert path(booking(client, room_numbers="101", offset=20)) == "/rooms"
    assert Reservations.query.count() == 3
