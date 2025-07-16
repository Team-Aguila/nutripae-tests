from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def see_departamentos(driver):
    boton_ver = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//h3[normalize-space()='test departamento editado']/ancestor::div[contains(@class, 'p-4') and contains(@class, 'shadow-sm')]//div[contains(@class,'justify-end')]//button[1]"
        ))
    )
    boton_ver.click()

def verify_rout_departamentos(driver, nombre_departamento="test departamento editado"):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//ol[@data-slot='breadcrumb-list']//span[@data-slot='breadcrumb-page' and normalize-space()='{nombre_departamento}']"
            ))
        )
        print(f"✅ Página de detalle del departamento '{nombre_departamento}' detectada.")
    except:
        print(f"❌ No se detectó la página de detalle del departamento '{nombre_departamento}'.")