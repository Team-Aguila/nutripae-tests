from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def seleccionar_departamento(driver, nombre="Antioquia"):
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

def data_create_municipio(driver):
    name = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "name"))
    )
    seleccionar_departamento(driver, "Antioquia")
    dane_code = driver.find_element(By.ID, "dane_code")
    btn = driver.find_element(By.XPATH, "//button[normalize-space()='Guardar']")

    name.send_keys("Guatape")
    dane_code.send_keys("456")
    btn.click()

def verify_toast_success(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//li[@data-type='success' and @data-visible='true']"
            ))
        )
        print("✅ Toast de éxito visible.")
    except:
        print("❌ No se detectó el toast de éxito.")
