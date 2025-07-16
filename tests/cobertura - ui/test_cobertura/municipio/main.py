import time
from test_cobertura.municipio.utils.data_municipios import data_create_municipio
from test_cobertura.municipio.utils.delete_municipios import delete_municipio_button
from test_cobertura.municipio.utils.edit_municipios import edit_municipio_data
from test_cobertura.municipio.utils.open_button_create_municipios import open_create_municipio, verify_open_dialog_create_municipio
from test_cobertura.municipio.utils.open_button_delete_municipios import open_buttton_delete_municipio, verify_open_dialog_delete_municipio
from test_cobertura.municipio.utils.open_button_edit_municipios import open_buttton_edit_municipio, verify_edit_municipio_page
from test_cobertura.municipio.utils.open_button_see_municipios import see_municipio, verify_rout_municipio
from utils.chrome_preferences import set_chrome_preferences
from utils.login import login
from utils.verify_toast import verify_toast_success



def run_selenium_script():
    driver = set_chrome_preferences()
    driver.get("http://localhost:5173/login")
    login(driver)
    time.sleep(3)
    driver.get("http://localhost:5173/coverage/towns")
    time.sleep(3)
    open_create_municipio(driver)
    verify_open_dialog_create_municipio(driver)
    data_create_municipio(driver)
    verify_toast_success(driver)
    time.sleep(3)
    open_buttton_edit_municipio(driver)
    verify_edit_municipio_page(driver)
    edit_municipio_data(driver)
    verify_toast_success(driver)
    see_municipio(driver)
    verify_rout_municipio(driver)
    driver.get("http://localhost:5173/coverage/towns")
    open_buttton_delete_municipio(driver)
    verify_open_dialog_delete_municipio(driver)
    delete_municipio_button(driver)
    verify_toast_success(driver)
    a = input("Presione Enter para continuar...")