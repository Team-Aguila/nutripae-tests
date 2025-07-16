from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def logout(driver):
    btn_options = driver.find_element(By.ID, "radix-«r6»")
    btn_options.click()
    btn_logout = driver.find_element(By.XPATH, "//div[@role='menuitem' and normalize-space()='Cerrar Sesión']")
    btn_logout.click()


def verify_logout(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        print("Logout successful.")
    except Exception as e:
        print("Logout failed:", e)