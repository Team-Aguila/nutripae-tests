from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def open_buttton_edit_municipio(driver):
    editar_btn = driver.find_element(
        By.XPATH,
        "//h3[normalize-space()='Guatape']/ancestor::div[contains(@class, 'p-4') and contains(@class, 'shadow-sm')]//div[contains(@class,'justify-end')]//button[2]"
    )
    editar_btn.click()
    

def verify_edit_municipio_page(driver):
    try:
        # Espera hasta que el título de la página sea visible
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.ID, "radix-«r9»")
            )
        )
        print("✅ Página de edición de municipio abierta correctamente.")
    except Exception as e:
        print("❌ No se pudo abrir la página de edición de municipio:", e)