from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def edit_municipio_data(driver):
    name_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name")))
    name_input.clear()
    name_input.send_keys("Nuevo Guatape")

    combo_button = driver.find_element(By.XPATH, "//button[@role='combobox']")
    combo_button.click()

    opcion_antioquia = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Tolima']"))
    )
    opcion_antioquia.click()

    guardar_btn = driver.find_element(By.XPATH, "//button[normalize-space()='Guardar']")
    guardar_btn.click()


def verify_toast_success(driver):
    try:
        # Espera hasta que el toast de éxito sea visible
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//li[@data-type='success' and @data-visible='true']")
            )
        )
        print("✅ Toast de éxito detectado.")
    except Exception as e:
        print("❌ No se detectó el toast de éxito:", e)