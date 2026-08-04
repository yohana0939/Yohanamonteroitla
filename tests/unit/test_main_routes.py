def test_home_page_devuelve_200_y_muestra_productos(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Productos destacados" in resp.data


def test_tienda_busqueda_filtra_resultados(client):
    resp = client.get("/tienda?buscar=Casio")
    assert resp.status_code == 200
    # Los 4 relojes Casio del catálogo semilla; la categoría "Perfumes"
    # sigue apareciendo en el <select> de filtro, así que no se puede
    # comprobar su ausencia en todo el HTML.
    assert resp.data.count(b"producto-card") == 4


def test_tienda_filtro_categoria(client):
    resp = client.get("/tienda?categoria=Perfumes")
    assert resp.status_code == 200
    assert resp.data.count(b"producto-card") == 5


def test_tienda_sin_resultados_muestra_mensaje(client):
    resp = client.get("/tienda?buscar=xyznoexiste")
    assert b"No se encontraron productos" in resp.data


def test_producto_detalle_200(client):
    resp = client.get("/producto/1")
    assert resp.status_code == 200


def test_producto_detalle_404_si_no_existe(client):
    resp = client.get("/producto/9999")
    assert resp.status_code == 404


def test_acerca_200(client):
    resp = client.get("/acerca")
    assert resp.status_code == 200


def test_ruta_desconocida_devuelve_404(client):
    resp = client.get("/no-existe")
    assert resp.status_code == 404
