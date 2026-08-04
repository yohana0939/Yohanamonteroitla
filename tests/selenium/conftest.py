import os
import tempfile
import threading
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from werkzeug.serving import make_server

from app import create_app
from app.extensions import db

HOST = "127.0.0.1"
PORT = 5005


class ServerThread(threading.Thread):
    def __init__(self, flask_app):
        super().__init__(daemon=True)
        self.server = make_server(HOST, PORT, flask_app)

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


@pytest.fixture(scope="session")
def base_url():
    return f"http://{HOST}:{PORT}"


@pytest.fixture(scope="session")
def live_server():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    flask_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
    })

    server = ServerThread(flask_app)
    server.start()
    time.sleep(0.5)

    yield flask_app

    server.shutdown()
    with flask_app.app_context():
        db.engine.dispose()
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture(scope="session")
def driver():
    opciones = Options()
    opciones.add_argument("--headless=new")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--window-size=1280,900")
    navegador = webdriver.Chrome(options=opciones)
    yield navegador
    navegador.quit()


@pytest.fixture(autouse=True)
def _sesion_limpia(driver, live_server, base_url):
    driver.get(base_url)
    driver.delete_all_cookies()
    yield
