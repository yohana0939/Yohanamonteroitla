def test_registro_crea_usuario_y_inicia_sesion(client):
    resp = client.post(
        "/registro",
        data={
            "nombre": "Nuevo Usuario",
            "email": "nuevo@test.com",
            "password": "clave123",
            "confirmar": "clave123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Bienvenido/a".encode() in resp.data


def test_registro_falla_si_contrasenas_no_coinciden(client):
    resp = client.post(
        "/registro",
        data={"nombre": "X", "email": "x@test.com", "password": "clave123", "confirmar": "otra456"},
        follow_redirects=True,
    )
    assert "no coinciden".encode() in resp.data


def test_registro_falla_con_correo_duplicado(client, app):
    datos = {"nombre": "Dup", "email": "dup@test.com", "password": "clave123", "confirmar": "clave123"}
    client.post("/registro", data=datos, follow_redirects=True)

    # Un segundo cliente (sesión propia, no autenticada) intenta registrarse
    # con el mismo correo; si se reusara el mismo `client` ya logueado, la
    # ruta /registro redirige de inmediato sin llegar a validar el correo.
    otro_client = app.test_client()
    resp = otro_client.post("/registro", data=datos, follow_redirects=True)
    assert "Ya existe una cuenta".encode() in resp.data


def test_registro_falla_con_contrasena_corta(client):
    resp = client.post(
        "/registro",
        data={"nombre": "Y", "email": "y@test.com", "password": "123", "confirmar": "123"},
        follow_redirects=True,
    )
    assert "al menos 6 caracteres".encode() in resp.data


def test_login_correcto(client):
    resp = client.post(
        "/login", data={"email": "admin@yanghstore.com", "password": "admin123"}, follow_redirects=True
    )
    assert "Hola de nuevo".encode() in resp.data


def test_login_password_incorrecto(client):
    resp = client.post(
        "/login", data={"email": "admin@yanghstore.com", "password": "mala"}, follow_redirects=True
    )
    assert "incorrectos".encode() in resp.data


def test_logout(admin_client):
    resp = admin_client.get("/logout", follow_redirects=True)
    assert "Sesión cerrada".encode() in resp.data
