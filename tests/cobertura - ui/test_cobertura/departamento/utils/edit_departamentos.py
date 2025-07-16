from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def edit_departmentos_data(driver):
    name = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "name")))
    btn = driver.find_element(By.XPATH, "//button[normalize-space()='Guardar']")
    
    name.send_keys("test departamento editado")
    btn.click()

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
