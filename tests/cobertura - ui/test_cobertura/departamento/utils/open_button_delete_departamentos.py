from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def open_delete_departamentos(driver):
    eliminar_btn = driver.find_element(
    By.XPATH,
    "//h3[normalize-space()='test departamento editado']/ancestor::div[contains(@class, 'p-4') and contains(@class, 'shadow-sm')]//div[contains(@class,'justify-end')]//button[3]"
)
    eliminar_btn.click()


def verify_open_dialog_delete_departamentos(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«rc»"))
        )
        print("Dialogo de eliminar departamento abierto correctamente.")
    except Exception as e:
        print("Error al abrir el dialogo de eliminar departamento:", e)