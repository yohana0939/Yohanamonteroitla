from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_home_page_carga_y_muestra_hero(driver, base_url):
    driver.get(base_url)
    assert "Yangh Store" in driver.title
    driver.find_element(By.CLASS_NAME, "hero")


def test_busqueda_en_tienda_filtra_productos(driver, base_url):
    driver.get(f"{base_url}/tienda")
    campo = driver.find_element(By.NAME, "buscar")
    campo.send_keys("Casio")
    campo.submit()

    tarjetas = WebDriverWait(driver, 10).until(
        lambda d: d.find_elements(By.CLASS_NAME, "producto-card") or None
    )
    assert len(tarjetas) > 0
    for tarjeta in tarjetas:
        assert "Casio" in tarjeta.text


def test_ver_detalle_de_producto(driver, base_url):
    driver.get(f"{base_url}/tienda")
    enlace = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".producto-card h3 a"))
    )
    titulo_esperado = enlace.text
    enlace.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    assert titulo_esperado in driver.find_element(By.TAG_NAME, "h1").text


def test_agregar_al_carrito_actualiza_el_contador(driver, base_url):
    driver.get(f"{base_url}/tienda")
    boton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".producto-card form button"))
    )
    boton.click()

    badge = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "cart-badge"))
    )
    assert badge.text == "1"

    driver.get(f"{base_url}/carrito")
    assert "carrito está vacío" not in driver.page_source
