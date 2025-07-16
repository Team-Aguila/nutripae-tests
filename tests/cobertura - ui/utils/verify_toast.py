from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def verify_toast_success(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//li[@data-type='success' and @data-visible='true']"
            ))
        )
        print("✅ Toast de éxito visible.")
    except:
        print("❌ No se detectó el toast de éxito.")