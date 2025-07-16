import time
from test_cobertura.instituciones_educativas.inits.data_IE import data_create_IE, verify_toast_success
from test_cobertura.instituciones_educativas.inits.delete_IE import delete_IE_button
from test_cobertura.instituciones_educativas.inits.edit_IE import edit_IE_data
from test_cobertura.instituciones_educativas.inits.go_IE import go_Instituciones_Educativas, verify_dialog_IE
from test_cobertura.instituciones_educativas.inits.open_button_create_IE import open_button_create_IE, verify_open_dialog_create_IE
from test_cobertura.instituciones_educativas.inits.open_button_delete_IE import open_buttton_delete_IE, verify_open_dialog_delete_ie
from test_cobertura.instituciones_educativas.inits.open_button_edit_IE import open_buttton_edit_IE, verify_edit_IE_page
from test_cobertura.instituciones_educativas.inits.open_button_see import open_buttton_see_IE, verify_root_IE
from utils.chrome_preferences import set_chrome_preferences
from utils.login import login

def run_selenium_script():
    driver = set_chrome_preferences()
    driver.get("http://localhost:5173/login")
    #login
    login(driver)
    time.sleep(3)
    # Navigate to IE
    go_Instituciones_Educativas(driver)
    verify_dialog_IE(driver)
    # Open the create Instituciones Educativas dialog
    time.sleep(3)
    open_button_create_IE(driver)
    verify_open_dialog_create_IE(driver)
    data_create_IE(driver)
    verify_toast_success(driver)
    # edit
    open_buttton_edit_IE(driver)
    verify_edit_IE_page(driver)
    edit_IE_data(driver)
    verify_toast_success(driver)
    # see IE
    time.sleep(3)
    open_buttton_see_IE(driver)
    time.sleep(3)
    verify_root_IE(driver)
    # back to IE
    go_Instituciones_Educativas(driver)
    verify_dialog_IE(driver)
    # delete
    open_buttton_delete_IE(driver)
    verify_open_dialog_delete_ie(driver)
    delete_IE_button(driver)
    verify_toast_success(driver)
    a = input("Press Enter to close the browser...")