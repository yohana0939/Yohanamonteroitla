def _crear_pedido_y_asignar(admin_client, cliente_client):
    cliente_client.post("/carrito/agregar/1", data={"cantidad": 1}, follow_redirects=True)
    cliente_client.post("/pago", data={"metodo_pago": "tarjeta"}, follow_redirects=True)
    admin_client.post(
        "/admin/pedidos/1", data={"estado": "Procesando", "despachador_id": "2"}, follow_redirects=True
    )


def test_cliente_no_puede_entrar_al_panel_de_despacho(cliente_client):
    resp = cliente_client.get("/despacho/")
    assert resp.status_code == 403


def test_despachador_ve_solo_sus_pedidos_asignados(admin_client, despachador_client, cliente_client):
    _crear_pedido_y_asignar(admin_client, cliente_client)

    resp = despachador_client.get("/despacho/")
    assert resp.status_code == 200
    assert b"#1" in resp.data


def test_despachador_puede_actualizar_estado_de_su_pedido(admin_client, despachador_client, cliente_client):
    _crear_pedido_y_asignar(admin_client, cliente_client)

    resp = despachador_client.post(
        "/despacho/pedidos/1/estado", data={"estado": "Enviado"}, follow_redirects=True
    )
    # Jinja escapa las comillas simples como &#39; en el HTML renderizado.
    assert "actualizado a &#39;Enviado&#39;".encode() in resp.data


def test_despachador_no_puede_tocar_pedido_ajeno(despachador_client, cliente_client):
    cliente_client.post("/carrito/agregar/1", data={"cantidad": 1}, follow_redirects=True)
    cliente_client.post("/pago", data={"metodo_pago": "tarjeta"}, follow_redirects=True)
    # El pedido #1 no tiene despachador asignado

    resp = despachador_client.post(
        "/despacho/pedidos/1/estado", data={"estado": "Enviado"}, follow_redirects=True
    )
    assert resp.status_code == 403


def test_admin_ve_el_panel_de_despacho(admin_client, despachador_client, cliente_client):
    _crear_pedido_y_asignar(admin_client, cliente_client)

    resp = admin_client.get("/despacho/")
    assert resp.status_code == 200
    assert b"#1" in resp.data
