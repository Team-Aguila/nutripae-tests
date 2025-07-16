from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def open_buttton_see_IE(driver):
    xpath = f"//h3[normalize-space()='{"test IE editado"}']/ancestor::div[contains(@class, 'p-4') and contains(@class, 'shadow-sm')]//div[contains(@class,'justify-end')]//button[1]"
    btn = driver.find_element(By.XPATH, xpath)
    btn.click()

def verify_root_IE(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH, "//h2[contains(normalize-space(), 'Sedes de')]"
            ))
        )
        print("✅ Página de visualización de IE abierta correctamente.")
    except Exception as e:
        print("❌ No se pudo abrir la página de visualización de IE:", e)