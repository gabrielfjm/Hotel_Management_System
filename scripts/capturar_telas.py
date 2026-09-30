"""Evidência de instalação e execução: sobe o sistema e captura as telas principais.

Uso (na raiz do repositório; o Playwright usa o Microsoft Edge já instalado):

    uv run --with playwright==1.55.0 python scripts/capturar_telas.py

Para cada versão (tag sut-original e working tree corrigida), extrai o código
em uma pasta temporária, cria uma base SQLite de demonstração com
scripts/seed_demo.py, inicia o servidor Flask na porta 5055 com o Python de
.venv e percorre: início, login, lista de quartos, consulta de
disponibilidade, reserva e "My Account". As imagens vão para evidencias/telas/.
"""

from datetime import date, timedelta
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
SAIDA = ROOT / "evidencias" / "telas"
PORTA = 5055
BASE = f"http://127.0.0.1:{PORTA}"


def extrair(versao, destino):
    if versao == "original":
        tar_bytes = subprocess.run(["git", "archive", "--format=tar", "sut-original"], cwd=ROOT,
                                   check=True, capture_output=True).stdout
        with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tar:
            tar.extractall(destino, filter="data")
    else:
        for nome in ("app.py", "compat.py"):
            shutil.copy2(ROOT / nome, destino / nome)
        shutil.copytree(ROOT / "hotel", destino / "hotel", ignore=shutil.ignore_patterns("*.db", "__pycache__"))
        shutil.copytree(ROOT / "scripts", destino / "scripts", ignore=shutil.ignore_patterns("__pycache__"))


def esperar_servidor():
    for _ in range(60):
        try:
            urllib.request.urlopen(BASE + "/", timeout=1)
            return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("Servidor não respondeu")


def data(dias):
    return (date.today() + timedelta(days=dias)).strftime("%m/%d/%Y")


def percorrer(page, prefixo):
    def foto(nome):
        page.screenshot(path=str(SAIDA / f"{prefixo}-{nome}.png"), full_page=nome.endswith("minha-conta"))

    page.goto(BASE + "/")
    foto("01-inicio")
    page.goto(BASE + "/signin")
    page.fill("input[name=email]", "ana@example.test")
    page.fill("input[name=password]", "senha123")
    foto("02-login")
    page.click("input[type=submit], button[type=submit]")
    page.wait_for_url("**/rooms")
    foto("03-quartos")
    page.goto(BASE + "/available")
    page.fill("input[name=checkin_date]", data(20))
    page.fill("input[name=checkout_date]", data(22))
    page.fill("input[name=num_guests]", "4")
    foto("04-consulta-formulario")
    page.click("input[type=submit], button[type=submit]")
    page.wait_for_load_state()
    foto("05-consulta-resultado")
    # Reserva do quarto 101 em período sem interseção com a reserva de demonstração (D+10 a D+12).
    page.goto(BASE + "/reserve")
    page.fill("input[name=checkin_date]", data(20))
    page.fill("input[name=checkout_date]", data(22))
    page.fill("input[name=num_guests]", "2")
    page.fill("input[name=room_numbers]", "101")
    foto("06-reserva-formulario")
    page.click("input[type=submit], button[type=submit]")
    page.wait_for_load_state()
    foto("07-reserva-resultado")
    page.goto(BASE + "/about_user")
    foto("08-minha-conta")


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge")
        for versao in ("original", "corrigida"):
            with tempfile.TemporaryDirectory() as pasta:
                pasta = Path(pasta)
                extrair(versao, pasta)
                env = {**os.environ, "HOTEL_DB_URI": f"sqlite:///{(pasta / 'demo.db').as_posix()}",
                       "PYTHONIOENCODING": "utf-8"}
                subprocess.run([str(PYTHON), "-m", "scripts.seed_demo"], cwd=pasta, env=env, check=True)
                servidor = subprocess.Popen(
                    [str(PYTHON), "-c", f"import compat; from hotel import app; app.run(port={PORTA})"],
                    cwd=pasta, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                try:
                    esperar_servidor()
                    pagina = navegador.new_page(viewport={"width": 1280, "height": 560})
                    percorrer(pagina, versao)
                    pagina.close()
                finally:
                    servidor.terminate()
                    servidor.wait(timeout=10)
        navegador.close()
    print(f"Telas em {SAIDA}")


if __name__ == "__main__":
    sys.exit(main())
