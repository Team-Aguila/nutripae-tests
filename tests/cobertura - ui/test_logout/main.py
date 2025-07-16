import time
from selenium import webdriver
from utils.login import login 
from test_logout.utils import logout
from utils.chrome_preferences import set_chrome_preferences
def run_selenium_script():
    driver = set_chrome_preferences()
    driver.get("http://localhost:5173/login")
    login(driver)    
    time.sleep(10)
    logout.logout(driver)
    print("Logout finisher.")
    logout.verify_logout(driver)
    print("verification complete.")
    a= input("Presione Enter para continuar...")
    
run_selenium_script()