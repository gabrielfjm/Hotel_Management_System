"""Lista as tabelas do SQLite e algumas linhas sem alterar os dados."""

import argparse
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "hotel" / "hotel_local.db"
parser = argparse.ArgumentParser()
parser.add_argument("--tabela", help="Mostra apenas uma tabela específica")
parser.add_argument("--limite", type=int, default=20)
args = parser.parse_args()

if not DATABASE.exists():
    raise SystemExit("Base ausente. Execute: .venv/Scripts/python.exe scripts/seed_demo.py")

connection = sqlite3.connect(f"file:{DATABASE.as_posix()}?mode=ro", uri=True)
connection.row_factory = sqlite3.Row
tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
print(f"Banco: {DATABASE}")
print("Tabelas:", ", ".join(tables))
selected = [args.tabela] if args.tabela else ["user", "rooms", "reservations", "booked", "payment"]
for table in selected:
    if table not in tables:
        raise SystemExit(f"Tabela inexistente: {table}")
    quoted = '"' + table.replace('"', '""') + '"'
    rows = connection.execute(f"SELECT * FROM {quoted} LIMIT ?", (args.limite,)).fetchall()
    print(f"\n[{table}] ({len(rows)} linhas exibidas)")
    for row in rows:
        values = dict(row)
        if "password" in values:
            values["password"] = "***"
        if "card_number" in values:
            values["card_number"] = "***"
        print(values)
