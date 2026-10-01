"""Base isolada para cada caso de teste e marcas de rastreabilidade.

Versão do sistema sob teste (SUT):

* ``SUT_VERSAO=corrigida`` (padrão): importa ``hotel/`` deste repositório.
* ``SUT_VERSAO=original``: importa ``.sut-original/hotel``, extraído da tag
  ``sut-original`` por ``etapas.ps1``. Nessa versão, cada caso marcado com
  ``@pytest.mark.defeito("DEF-xx", ...)`` recebe ``xfail(strict=True)``: o teste
  precisa falhar para confirmar que o defeito existe no código original.

Marcas usadas:

* ``funcional``, ``estrutural``, ``mutacao``: etapa em que o caso foi criado.
* ``ce("CE-01", ...)``: classes de equivalência exercitadas.
* ``defeito("DEF-01", "descrição")``: defeito que o caso revela no original.
"""

from datetime import date, datetime, timedelta
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
SUT_VERSAO = os.environ.get("SUT_VERSAO", "corrigida")
if SUT_VERSAO == "original":
    original = ROOT / ".sut-original"
    if not (original / "hotel" / "views.py").exists():
        raise RuntimeError("Execute etapas.ps1 (ou git archive sut-original hotel) para extrair o SUT original.")
    sys.path.insert(0, str(original))
elif SUT_VERSAO != "corrigida":
    raise RuntimeError("SUT_VERSAO deve ser 'original' ou 'corrigida'.")

os.environ["HOTEL_DB_URI"] = "sqlite://"
import compat  # noqa: E402,F401 - deve ser carregado antes de hotel
from hotel import app  # noqa: E402
from hotel.models import Booked, Payment, Reservations, Room_type, Rooms, User, db  # noqa: E402
from hotel import views  # noqa: E402


def pytest_addoption(parser):
    parser.addoption("--rastreabilidade", metavar="ARQUIVO",
                     help="grava em JSON o caso, a etapa, as classes e os defeitos de cada teste")


def pytest_report_header(config):
    return f"SUT_VERSAO={SUT_VERSAO}; hotel.views={Path(views.__file__).resolve()}"


def pytest_collection_modifyitems(config, items):
    matrix = []
    for item in items:
        marker = item.get_closest_marker("defeito")
        defect = list(marker.args) if marker else []
        if marker and SUT_VERSAO == "original":
            item.add_marker(pytest.mark.xfail(strict=True, reason=": ".join(defect)))
        ce = item.get_closest_marker("ce")
        stage = next((name for name in ("funcional", "estrutural", "mutacao", "secundario") if item.get_closest_marker(name)), "")
        case = re.search(r"CT_(\d{3})", item.name)
        matrix.append({
            "caso": f"CT-{case.group(1)}" if case else "",
            "teste": item.nodeid,
            "etapa": stage,
            "classes": list(ce.args) if ce else [],
            "defeito": defect[0] if defect else "",
        })
    path = config.getoption("--rastreabilidade")
    if path:
        Path(path).write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")


@pytest.fixture
def baseline():
    """Três quartos (101: R$100/2 pessoas; 102: R$150/3; 301: R$200/4) e dois usuários."""
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    db.session.remove()
    db.drop_all()
    db.create_all()
    if hasattr(views, "global_avail"):
        views.global_avail = None

    room_type = Room_type("Padrão", "Quarto de teste")
    owner = User("Ana", "Silva", "ana", "senha123", "ana@example.test")
    other = User("Bruno", "Costa", "bruno", "senha123", "bruno@example.test")
    db.session.add_all([room_type, owner, other])
    db.session.commit()
    for number, cost, capacity in [(101, 100, 2), (102, 150, 3), (301, 200, 4)]:
        room = Rooms(room_type.tid, cost, capacity, "available")
        room.room_number = number
        db.session.add(room)
    db.session.commit()
    yield {"ana": owner.uid, "bruno": other.uid}
    if hasattr(views, "global_avail"):
        views.global_avail = None
    db.session.remove()
    db.drop_all()


@pytest.fixture
def client(baseline):
    return app.test_client()


def login(client, username="ana"):
    with client.session_transaction() as session:
        session["user_available"] = True
        session["current_user"] = username


def path(response):
    """Caminho do redirecionamento (ex.: '/rooms'), independente do host."""
    return urlparse(response.location).path


def stay(offset=10, nights=2):
    start = date.today() + timedelta(days=offset)
    end = start + timedelta(days=nights)
    return start, end


def form_dates(start, end):
    return {"checkin_date": start.strftime("%m/%d/%Y"), "checkout_date": end.strftime("%m/%d/%Y")}


def booking(client, room_numbers="101", guests="2", offset=10, nights=2):
    start, end = stay(offset, nights)
    payload = form_dates(start, end)
    payload.update(num_guests=guests, room_numbers=room_numbers)
    return client.post("/reserve", data=payload)


def availability(client, guests="2", offset=10, nights=2):
    start, end = stay(offset, nights)
    return client.post("/available", data={**form_dates(start, end), "num_guests": guests})


def listed_rooms(client):
    """Números de quarto exibidos em /rooms."""
    response = client.get("/rooms")
    assert response.status_code == 200
    return sorted(int(n) for n in re.findall(rb"Room Number: (\d+)", response.data))


def seed_reservation(user_id, room_numbers=(101,), offset=10, nights=2, guests=2, cost=200):
    start, end = stay(offset, nights)
    reservation = Reservations(user_id, start, end, guests, cost)
    db.session.add(reservation)
    db.session.commit()
    for room in room_numbers:
        db.session.add(Booked(reservation.rid, room))
    db.session.commit()
    return reservation.rid


# ------------------------------------------------ auxiliares com datas reais (casos principais)
# As datas são escritas como no Brasil (DD/MM/AAAA). O formulário do sistema usa MM/DD/AAAA.

def hoje(dias=0):
    """Data relativa ao dia da execução, para os casos de 'hoje' e 'ontem' (DD/MM/AAAA)."""
    return (date.today() + timedelta(days=dias)).strftime("%d/%m/%Y")


def _data(texto):
    return datetime.strptime(texto, "%d/%m/%Y").date()


def reservar(client, quartos="101", hospedes=2, entrada="10/03/2030", saida="12/03/2030"):
    """Envia o formulário de reserva (POST /reserve) como a usuária logada."""
    return client.post("/reserve", data={
        "room_numbers": quartos, "num_guests": str(hospedes),
        "checkin_date": _data(entrada).strftime("%m/%d/%Y"), "checkout_date": _data(saida).strftime("%m/%d/%Y"),
    })


def reserva_existente(usuario, quartos=(101,), entrada="10/03/2030", saida="12/03/2030", hospedes=2, custo=200):
    """Grava direto no banco uma reserva que já existia antes do teste."""
    reservation = Reservations(usuario, _data(entrada), _data(saida), hospedes, custo)
    db.session.add(reservation)
    db.session.commit()
    for quarto in quartos:
        db.session.add(Booked(reservation.rid, quarto))
    db.session.commit()
    return reservation.rid


def consultar(client, hospedes=2, entrada="10/03/2030", saida="12/03/2030"):
    """Envia o formulário de consulta de disponibilidade (POST /available)."""
    return client.post("/available", data={
        "num_guests": str(hospedes),
        "checkin_date": _data(entrada).strftime("%m/%d/%Y"), "checkout_date": _data(saida).strftime("%m/%d/%Y"),
    })


def seed_payment(user_id, rid):
    db.session.add(Payment(user_id, rid, "Ana Silva", 1234, "Confirmed"))
    db.session.commit()
