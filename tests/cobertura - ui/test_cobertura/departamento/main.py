import time

from test_cobertura.departamento.utils.data_departamentos import data_create_departamentos
from test_cobertura.departamento.utils.delete_departamentos import delete_departamento_button
from test_cobertura.departamento.utils.edit_departamentos import edit_departmentos_data
from test_cobertura.departamento.utils.open_button_create_departamentos import open_create_departamentos
from test_cobertura.departamento.utils.open_button_delete_departamentos import open_delete_departamentos, verify_open_dialog_delete_departamentos
from test_cobertura.departamento.utils.open_button_edit_departamentos import open_edit_departamentos, verify_edit_departamentos_page
from test_cobertura.departamento.utils.open_button_see_departamentos import see_departamentos, verify_rout_departamentos
from utils.chrome_preferences import set_chrome_preferences
from utils.login import login
from utils.verify_toast import verify_toast_success



def run_selenium_script():
    driver = set_chrome_preferences()
    driver.get("http://localhost:5173/login")
    login(driver)
    time.sleep(3)
    driver.get("http://localhost:5173/coverage/departments")
    time.sleep(3)
    open_create_departamentos(driver)
    data_create_departamentos(driver)
    verify_toast_success(driver)
    time.sleep(3)
    open_edit_departamentos(driver)
    verify_edit_departamentos_page(driver)
    edit_departmentos_data(driver)
    verify_toast_success(driver)
    see_departamentos(driver)
    verify_rout_departamentos(driver)
    driver.get("http://localhost:5173/coverage/departments")
    time.sleep(3)
    open_delete_departamentos(driver)
    verify_open_dialog_delete_departamentos(driver)
    delete_departamento_button(driver)
    verify_toast_success(driver)