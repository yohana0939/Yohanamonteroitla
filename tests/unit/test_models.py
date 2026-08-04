from app.models import User
from app.utils import slugify


def test_password_hashing_no_guarda_texto_plano():
    usuario = User(nombre="Ana", email="ana@test.com")
    usuario.set_password("clave-secreta")

    assert usuario.password_hash != "clave-secreta"
    assert usuario.check_password("clave-secreta")
    assert not usuario.check_password("otra-clave")


def test_rol_por_defecto_es_cliente(app):
    with app.app_context():
        from app.extensions import db

        usuario = User(nombre="Ana", email="ana2@test.com")
        usuario.set_password("clave123")
        db.session.add(usuario)
        db.session.commit()

        assert usuario.rol == "cliente"


def test_slugify_normaliza_texto():
    assert slugify("Reloj Casio G-Shock") == "reloj-casio-g-shock"
    assert slugify("Aire Acondicionado 12000 BTU") == "aire-acondicionado-12000-btu"
    assert slugify("Climatización") == "climatizacion"
