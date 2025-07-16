import os
import re
import glob
import time
import shutil
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import test_logout.utils.logout as logout
def login(driver):
    user = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email")))
    password = driver.find_element(By.ID, "password")
    btn = driver.find_element(By.XPATH, "//button[normalize-space()='Iniciar sesión']")

    user.send_keys("admin@test.com")
    password.send_keys("Password123!")
    btn.click()
