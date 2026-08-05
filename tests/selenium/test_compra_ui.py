from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _registrar_usuario(driver, base_url, nombre, email, password):
    driver.get(f"{base_url}/registro")
    driver.find_element(By.NAME, "nombre").send_keys(nombre)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "confirmar").send_keys(password)
    driver.find_element(By.ID, "terminos").click()
    driver.find_element(By.CSS_SELECTOR, "form button[type=submit]").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "hero")))


def test_flujo_completo_de_compra_por_la_interfaz(driver, base_url):
    _registrar_usuario(driver, base_url, "Selenium Comprador", "comprador.selenium@test.com", "compra123")

    driver.get(f"{base_url}/tienda")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".producto-card form button"))
    ).click()

    driver.get(f"{base_url}/carrito")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Finalizar compra"))
    ).click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "titular")))
    driver.find_element(By.NAME, "titular").send_keys("Selenium Comprador")
    driver.find_element(By.NAME, "numero_tarjeta").send_keys("4111111111111111")
    vencimiento = driver.find_element(By.NAME, "vencimiento")
    driver.execute_script("arguments[0].value = '2030-12';", vencimiento)
    driver.find_element(By.NAME, "cvv").send_keys("123")
    driver.find_element(By.CSS_SELECTOR, "form button.btn-accent").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tracker-steps")))
    assert "Pedido #" in driver.find_element(By.TAG_NAME, "h1").text

    driver.get(f"{base_url}/mis-pedidos")
    assert "#1" in driver.page_source


def test_checkout_exige_inicio_de_sesion(driver, base_url):
    driver.get(f"{base_url}/tienda")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".producto-card form button"))
    ).click()

    driver.get(f"{base_url}/pago")
    WebDriverWait(driver, 10).until(EC.url_contains("/login"))
    assert "/login" in driver.current_url
