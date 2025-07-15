from selenium import webdriver


class DriverManager:
    driver = None

    def __init__(self, browserName: str):
        if browserName.lower() == "chrome":
            self.driver = webdriver.Chrome()
        elif browserName.lower() == "firefox":
            self.driver = webdriver.Firefox()
        else:
            raise ValueError(f"Unsupported browser: {browserName}")

    def get_driver(self) -> webdriver.Remote | None:
        return self.driver

    def close_driver(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
        else:
            raise Exception(
                "Driver is not initialized. Cannot close a non-existent driver."
            )
