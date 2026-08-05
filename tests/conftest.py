import os
import tempfile

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    flask_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
    })

    yield flask_app

    with flask_app.app_context():
        db.engine.dispose()
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_client(app):
    cliente = app.test_client()
    cliente.post(
        "/login",
        data={"email": "admin@yanghstore.com", "password": "admin123"},
        follow_redirects=True,
    )
    return cliente


@pytest.fixture
def despachador_client(app):
    cliente = app.test_client()
    cliente.post(
        "/login",
        data={"email": "despachador@yanghstore.com", "password": "despacho123"},
        follow_redirects=True,
    )
    return cliente


@pytest.fixture
def cliente_client(app):
    cliente = app.test_client()
    cliente.post(
        "/registro",
        data={
            "nombre": "Cliente de Prueba",
            "email": "cliente.prueba@test.com",
            "password": "cliente123",
            "confirmar": "cliente123",
        },
        follow_redirects=True,
    )
    return cliente
