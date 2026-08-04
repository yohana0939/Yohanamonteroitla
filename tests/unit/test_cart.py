from app.models import Product


def test_agregar_al_carrito_y_verlo(cliente_client):
    cliente_client.post("/carrito/agregar/1", data={"cantidad": 2}, follow_redirects=True)
    resp = cliente_client.get("/carrito")
    assert resp.status_code == 200
    assert b"Reloj Casio F91W" in resp.data


def test_actualizar_cantidad_en_carrito(cliente_client):
    cliente_client.post("/carrito/agregar/1", data={"cantidad": 1}, follow_redirects=True)
    cliente_client.post("/carrito/actualizar/1", data={"cantidad": 3}, follow_redirects=True)
    resp = cliente_client.get("/carrito")
    assert b'value="3"' in resp.data


def test_eliminar_del_carrito(cliente_client):
    cliente_client.post("/carrito/agregar/1", data={"cantidad": 1}, follow_redirects=True)
    cliente_client.post("/carrito/eliminar/1", follow_redirects=True)
    resp = cliente_client.get("/carrito")
    assert "carrito está vacío".encode() in resp.data


def test_checkout_sin_login_redirige_a_login(client):
    resp = client.get("/pago")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_checkout_completo_crea_pedido_y_descuenta_stock(cliente_client, app):
    with app.app_context():
        stock_inicial = Product.query.get(1).stock

    cliente_client.post("/carrito/agregar/1", data={"cantidad": 2}, follow_redirects=True)
    resp = cliente_client.post("/pago", data={"metodo_pago": "tarjeta"}, follow_redirects=True)

    assert resp.status_code == 200
    assert "Pedido #1".encode() in resp.data

    with app.app_context():
        stock_final = Product.query.get(1).stock
        assert stock_final == stock_inicial - 2


def test_checkout_rechaza_si_no_hay_stock_suficiente(cliente_client):
    cliente_client.post("/carrito/agregar/1", data={"cantidad": 999999}, follow_redirects=True)
    resp = cliente_client.post("/pago", data={"metodo_pago": "tarjeta"}, follow_redirects=True)
    assert "No hay suficiente stock".encode() in resp.data


def test_carrito_se_vacia_tras_comprar(cliente_client):
    cliente_client.post("/carrito/agregar/2", data={"cantidad": 1}, follow_redirects=True)
    cliente_client.post("/pago", data={"metodo_pago": "tarjeta"}, follow_redirects=True)
    resp = cliente_client.get("/carrito")
    assert "carrito está vacío".encode() in resp.data


def test_seguimiento_de_pedido_muestra_tracker(cliente_client):
    cliente_client.post("/carrito/agregar/1", data={"cantidad": 1}, follow_redirects=True)
    cliente_client.post("/pago", data={"metodo_pago": "tarjeta"}, follow_redirects=True)
    resp = cliente_client.get("/pedido/1")
    assert resp.status_code == 200
    assert b"tracker-steps" in resp.data


def test_mis_pedidos_lista_pedidos_del_usuario(cliente_client):
    cliente_client.post("/carrito/agregar/1", data={"cantidad": 1}, follow_redirects=True)
    cliente_client.post("/pago", data={"metodo_pago": "tarjeta"}, follow_redirects=True)
    resp = cliente_client.get("/mis-pedidos")
    assert b"#1" in resp.data


def test_no_se_puede_ver_pedido_de_otro_usuario(cliente_client, app):
    cliente_client.post("/carrito/agregar/1", data={"cantidad": 1}, follow_redirects=True)
    cliente_client.post("/pago", data={"metodo_pago": "tarjeta"}, follow_redirects=True)

    otro = app.test_client()
    otro.post(
        "/registro",
        data={"nombre": "Otro", "email": "otro@test.com", "password": "otro12345", "confirmar": "otro12345"},
        follow_redirects=True,
    )
    resp = otro.get("/pedido/1")
    assert resp.status_code == 403
