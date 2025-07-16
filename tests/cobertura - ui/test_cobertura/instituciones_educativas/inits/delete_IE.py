from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def delete_IE_button(driver):
    eliminar_btn = driver.find_element(
        By.XPATH,
    "//button[normalize-space()='Confirmar']"
    )
    eliminar_btn.click()
