from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def delete_municipio_button(driver):
    eliminar_btn = driver.find_element(
        By.XPATH,
    "//button[normalize-space()='Confirmar']"
    )
    eliminar_btn.click()

def verify_toast_success(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//li[contains(@data-type, 'success') and @data-visible='true']"
            ))
        )
        print("✅ Toast de éxito detectado.")
        return True
    except:
        print("❌ No se detectó el toast.")
        return False