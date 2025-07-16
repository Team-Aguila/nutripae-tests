from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def seleccionar_institucion(driver, nombre="Aguirre Inc"):
    # 1. Clic en el combobox
    boton_combobox = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']"))
    )
    boton_combobox.click()

    # 2. Esperar la opción y seleccionarla
    opcion = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((
            By.XPATH, f"//div[@role='option' and normalize-space()='{nombre}']"
        ))
    )
    opcion.click()

def data_create_SE(driver):
    name = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "name"))
    )
    name.send_keys("test SE")
    dane_code = driver.find_element(By.ID, "dane_code")
    dane_code.send_keys("024680")
    address = driver.find_element(By.ID, "address")
    address.send_keys("Calle 123 #45-67")
    latitude = driver.find_element(By.ID, "latitude")
    latitude.send_keys("3.456789")
    longitude = driver.find_element(By.ID, "longitude")
    longitude.send_keys("76.543210")
    seleccionar_institucion(driver, "Aguirre Inc")
    btn = driver.find_element(By.XPATH, "//button[normalize-space()='Guardar']")
    btn.click()
