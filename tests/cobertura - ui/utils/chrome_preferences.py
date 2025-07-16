from selenium import webdriver

def set_chrome_preferences():
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safeBrowse.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)

    return driver