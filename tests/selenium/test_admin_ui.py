from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _login(driver, base_url, email, password):
    driver.get(f"{base_url}/login")
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "form button").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "hero")))


def test_admin_puede_crear_producto_desde_el_panel(driver, base_url):
    _login(driver, base_url, "admin@yanghstore.com", "admin123")

    driver.get(f"{base_url}/admin/productos/nuevo")
    driver.find_element(By.NAME, "titulo").send_keys("Producto Selenium")
    driver.find_element(By.NAME, "precio").send_keys("999")
    driver.find_element(By.NAME, "stock").send_keys("5")
    driver.find_element(By.NAME, "categoria").send_keys("Hogar")
    driver.find_element(By.NAME, "detalle").send_keys("Creado por prueba Selenium")
    driver.find_element(By.CSS_SELECTOR, "form button.btn-accent").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    assert "Producto Selenium" in driver.page_source


def test_despachador_no_puede_entrar_al_panel_admin(driver, base_url):
    _login(driver, base_url, "despachador@yanghstore.com", "despacho123")

    driver.get(f"{base_url}/admin/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    assert "403" in driver.find_element(By.TAG_NAME, "h1").text


def test_admin_puede_cambiar_rol_de_usuario(driver, base_url):
    _login(driver, base_url, "admin@yanghstore.com", "admin123")

    driver.get(f"{base_url}/admin/usuarios")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    assert "despachador@yanghstore.com" in driver.page_source
