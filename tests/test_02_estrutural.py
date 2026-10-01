"""Etapa 2 - teste estrutural (caixa-branca): reaproveitamento dos casos funcionais.

Nenhum caso novo é criado. Depois de medir com coverage.py (--cov-branch) a
cobertura dos 15 casos funcionais sobre hotel/views.py original, cinco deles
foram reaproveitados para desenhar e percorrer os grafos de fluxo de reserve:
CT-001 (reserva aceita), CT-005 (sem login), CT-009 (dado inválido),
CT-012 (quarto ocupado) e CT-013 (data no passado). Três desses casos foram
ampliados com o cenário que deixava trechos sem cobertura. Cada ampliação usa
o identificador do caso que amplia; o comentário indica as linhas/desvios do
código original que ela passou a cobrir. Meta: 100% dos comandos e 100% dos
desvios viáveis das funções do recorte (reserve e cal_cost).
"""

import pytest

from hotel.models import Booked, Reservations
from conftest import login, path, reserva_existente, reservar


estrutural = pytest.mark.estrutural


@estrutural
@pytest.mark.ce("CE-01", "CE-15")
def test_CT_001_ampliacao_formulario_aberto_antes_e_outro_quarto_ocupado(client, baseline):
    # Original: desvio 189->241 e linha 241 (abrir o formulário com GET, sem enviar) e
    # desvios 208->205 e 205->204 (reserva já existente de OUTRO quarto no mesmo período).
    reserva_existente(baseline["bruno"], quartos=(102,), entrada="10/03/2030", saida="12/03/2030")
    login(client)
    formulario = client.get("/reserve")
    assert formulario.status_code == 200
    assert b'name="room_numbers"' in formulario.data
    assert path(reservar(client, quartos="101", entrada="10/03/2030", saida="12/03/2030")) == "/rooms"
    assert Reservations.query.count() == 2


@estrutural
@pytest.mark.ce("CE-02")
def test_CT_005_ampliacao_usuario_que_saiu_nao_reserva(client):
    # Original: desvio 186->242 e linhas 242-243 (ramo falso de "if session['user_available']").
    # Sem a chave na sessão o original quebra antes do if; o ramo falso só roda depois de um logout.
    with client.session_transaction() as sessao:
        sessao["user_available"] = False
    assert path(client.get("/reserve")) == "/"
    assert path(reservar(client)) == "/"
    assert Reservations.query.count() == 0


@estrutural
@pytest.mark.ce("CE-15")
@pytest.mark.defeito("DEF-15", "vínculo de quarto é comparado com reservas de outros quartos")
def test_CT_012_ampliacao_reserva_de_outro_quarto_nao_bloqueia(client, baseline):
    # Lendo o laço triplo das linhas 203-212 para cobrir o desvio 208->205: ele combina cada
    # quarto reservado com as datas de TODAS as reservas (falta brid == rid). Aqui o 101 está
    # livre em 20/03, mas o original o recusa por causa da reserva do Bruno (quarto 102).
    reserva_existente(baseline["ana"], quartos=(101,), entrada="10/03/2030", saida="12/03/2030")
    reserva_existente(baseline["bruno"], quartos=(102,), entrada="20/03/2030", saida="22/03/2030")
    login(client)
    assert path(reservar(client, quartos="101", entrada="20/03/2030", saida="22/03/2030")) == "/rooms"
    assert Reservations.query.count() == 3


# Os casos CT-009 (dado inválido) e CT-013 (data no passado) foram reaproveitados sem ampliação:
# eles já percorrem os caminhos de recusa das linhas 223-225 e 230-232.
