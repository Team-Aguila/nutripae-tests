from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def open_create_departamentos(driver):
    agregar_btn = driver.find_element(By.XPATH, "//button[normalize-space()='Agregar departamento']")
    agregar_btn.click()

def verify_open_dialog_create_departamento(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«r9»"))
        )
        print("Create Departamento dialog opened successfully.")
    except Exception as e:
        print("Fail during the opening of the dialog in create departamento", e)