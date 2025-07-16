from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def open_button_create_IE(driver):
    agregar_btn = driver.find_element(By.XPATH, "//button[normalize-space()='Agregar Institución']")
    agregar_btn.click()

def verify_open_dialog_create_IE(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«r9»"))
        )
        print("Create Instituciones Educativas dialog opened successfully.")
    except Exception as e:
        print("Fail during the opening of the dialog in create Instituciones Educativas", e)