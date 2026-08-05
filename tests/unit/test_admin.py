from app.models import User


def test_admin_routes_redirige_a_login_si_no_autenticado(client):
    resp = client.get("/admin/")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_cliente_no_puede_acceder_a_admin(cliente_client):
    resp = cliente_client.get("/admin/")
    assert resp.status_code == 403


def test_despachador_no_puede_acceder_a_admin(despachador_client):
    resp = despachador_client.get("/admin/")
    assert resp.status_code == 403


def test_admin_dashboard_200(admin_client):
    resp = admin_client.get("/admin/")
    assert resp.status_code == 200
    assert b"Resumen" in resp.data


def test_admin_crea_producto(admin_client):
    resp = admin_client.post(
        "/admin/productos/nuevo",
        data={
            "titulo": "Producto de prueba",
            "precio": "100",
            "stock": "5",
            "categoria": "Hogar",
            "imagen": "difusor.svg",
            "detalle": "Descripción de prueba",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Producto de prueba".encode() in resp.data


def test_admin_rechaza_precio_invalido(admin_client):
    resp = admin_client.post(
        "/admin/productos/nuevo",
        data={
            "titulo": "Malo",
            "precio": "-10",
            "stock": "5",
            "categoria": "Hogar",
            "imagen": "difusor.svg",
            "detalle": "malo",
        },
        follow_redirects=True,
    )
    assert "El precio debe ser mayor a 0".encode() in resp.data


def test_admin_edita_producto(admin_client):
    resp = admin_client.post(
        "/admin/productos/1/editar",
        data={
            "titulo": "Reloj Editado",
            "precio": "2000",
            "stock": "10",
            "categoria": "Relojes",
            "imagen": "reloj.svg",
            "detalle": "Editado",
        },
        follow_redirects=True,
    )
    assert "Reloj Editado".encode() in resp.data


def test_admin_elimina_producto(admin_client):
    resp = admin_client.post("/admin/productos/1/eliminar", follow_redirects=True)
    assert "eliminado".encode() in resp.data


def test_admin_asigna_despachador_y_cambia_estado(admin_client, cliente_client):
    cliente_client.post("/carrito/agregar/2", data={"cantidad": 1}, follow_redirects=True)
    cliente_client.post("/pago", data={"metodo_pago": "tarjeta"}, follow_redirects=True)

    resp = admin_client.post(
        "/admin/pedidos/1",
        data={"estado": "Procesando", "despachador_id": "2"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "actualizado".encode() in resp.data

    resp = admin_client.get("/admin/pedidos/1")
    assert b"selected>Despachador Demo" in resp.data


def test_admin_cambia_rol_de_usuario(admin_client, cliente_client, app):
    with app.app_context():
        cliente_id = User.query.filter_by(email="cliente.prueba@test.com").first().id

    resp = admin_client.post(
        f"/admin/usuarios/{cliente_id}/rol", data={"rol": "despachador"}, follow_redirects=True
    )
    # Jinja escapa las comillas simples como &#39; en el HTML renderizado.
    assert "actualizado a &#39;despachador&#39;".encode() in resp.data


def test_admin_no_puede_cambiar_su_propio_rol(admin_client, app):
    with app.app_context():
        admin_id = User.query.filter_by(email="admin@yanghstore.com").first().id

    resp = admin_client.post(
        f"/admin/usuarios/{admin_id}/rol", data={"rol": "cliente"}, follow_redirects=True
    )
    assert "No puedes cambiar tu propio rol".encode() in resp.data
