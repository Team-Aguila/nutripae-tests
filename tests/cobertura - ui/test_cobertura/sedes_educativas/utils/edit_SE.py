from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def edit_SE_data(driver):
    name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name")))
    name.clear()
    name.send_keys("test SE editado")
    address = driver.find_element(By.ID, "address")
    address.clear()
    address.send_keys("Calle 765 # 43-21")
    latitude = driver.find_element(By.ID, "latitude")
    latitude.clear()
    latitude.send_keys("9.876543")
    longitude = driver.find_element(By.ID, "longitude")
    longitude.clear()
    longitude.send_keys("67.12345")
    combo_button = driver.find_element(By.XPATH, "//button[@role='combobox']")
    combo_button.click()
    another_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Amaya Ltd']"))
    )
    another_option.click()
    guardar_btn = driver.find_element(By.XPATH, "//button[normalize-space()='Guardar']")
    guardar_btn.click()