import time
from test_cobertura.sedes_educativas.utils.data_SE import data_create_SE
from test_cobertura.sedes_educativas.utils.delete_SE import delete_SE_button
from test_cobertura.sedes_educativas.utils.edit_SE import edit_SE_data
from test_cobertura.sedes_educativas.utils.open_botton_edit_SE import open_buttton_edit_SE, verify_edit_SE_page
from test_cobertura.sedes_educativas.utils.open_button_create_SE import open_button_create_SE, verify_open_dialog_create_SE
from test_cobertura.sedes_educativas.utils.open_button_delete_SE import open_button_delete_SE, verify_open_dialog_delete_SE
from utils.chrome_preferences import set_chrome_preferences
from utils.login import login
from utils.verify_toast import verify_toast_success


def run_selenium_script():
    driver = set_chrome_preferences()
    driver.get("http://localhost:5173/login")
    #login
    login(driver)
    time.sleep(3)
    # Navigate to SE
    driver.get("http://localhost:5173/coverage/campuses")
    time.sleep(3)
    # create SE
    open_button_create_SE(driver)
    verify_open_dialog_create_SE(driver)
    data_create_SE(driver)
    verify_toast_success(driver)
    # edit SE
    open_buttton_edit_SE(driver)
    verify_edit_SE_page(driver)
    edit_SE_data(driver)
    verify_toast_success(driver)
    # delete SE
    time.sleep(3)
    open_button_delete_SE(driver)
    verify_open_dialog_delete_SE(driver)
    delete_SE_button(driver)
    verify_toast_success(driver)
    a = input("Press Enter to close the browser...")