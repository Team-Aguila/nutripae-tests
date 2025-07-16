from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def data_create_departamentos(driver):
    name = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "name")))
    dane_code = driver.find_element(By.ID, "dane_code")
    btn = driver.find_element(By.XPATH, "//button[normalize-space()='Guardar']")

    name.send_keys("test departamento")
    dane_code.send_keys("11")
    btn.click()