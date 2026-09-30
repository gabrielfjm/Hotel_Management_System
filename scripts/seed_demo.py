"""Cria dados idempotentes no SQLite local, sem tocar na base dos testes."""

from datetime import date, timedelta

import compat  # noqa: F401
from hotel.models import Booked, Reservations, Room_type, Rooms, User, db


room_type = Room_type.query.filter_by(type_name="Padrão").first()
if room_type is None:
    room_type = Room_type("Padrão", "Quarto de demonstração")
    db.session.add(room_type)
    db.session.commit()

for firstname, lastname, username, email in [
    ("Ana", "Silva", "ana", "ana@example.test"),
    ("Bruno", "Costa", "bruno", "bruno@example.test"),
]:
    if User.query.filter_by(username=username).first() is None:
        db.session.add(User(firstname, lastname, username, "senha123", email))

for number, cost, capacity in [(101, 100, 2), (102, 150, 3), (103, 200, 4)]:
    if Rooms.query.get(number) is None:
        room = Rooms(room_type.tid, cost, capacity, "available")
        room.room_number = number
        db.session.add(room)
db.session.commit()

ana = User.query.filter_by(username="ana").first()
if Reservations.query.filter_by(ruid=ana.uid).count() == 0:
    start = date.today() + timedelta(days=10)
    end = start + timedelta(days=2)
    reservation = Reservations(ana.uid, start, end, 2, 200)
    db.session.add(reservation)
    db.session.commit()
    db.session.add(Booked(reservation.rid, 101))
    db.session.commit()

print("Base pronta: hotel/hotel_local.db")
print("Contas: ana@example.test / senha123; bruno@example.test / senha123")
