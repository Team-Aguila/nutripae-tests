from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def go_Instituciones_Educativas(driver):
    btn_cobertura = driver.find_element(By.XPATH, "//button[.//span[text()='Cobertura']]")
    btn_cobertura.click()
    Instituciones_Educativas_link = driver.find_element(By.XPATH, "//a[.//span[text()='Instituciones Educativas']]")
    Instituciones_Educativas_link.click()

def verify_dialog_IE(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Instituciones Educativas']"))
        )
        print("Instituciones Educativas page loaded successfully.")
    except Exception as e:
        print("Failed to load Instituciones Educativas page:", e)