from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from typing import Optional


class DriverManager:
    """
    Clase para gestionar el driver de Selenium de manera centralizada.
    """

    def __init__(self, browser_name: str):
        self.driver: Optional[webdriver.Remote] = None
        self._initialize_driver(browser_name)

    def _initialize_driver(self, browser_name: str) -> None:
        """
        Inicializa el driver según el navegador especificado.

        Args:
            browser_name (str): Nombre del navegador (chrome, firefox)

        Raises:
            ValueError: Si el navegador no está soportado
        """
        browser_name = browser_name.lower().strip()

        if browser_name == "chrome":
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            # Descomenta la siguiente línea para ejecutar en modo headless
            # chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(options=chrome_options)

        elif browser_name == "firefox":
            firefox_options = FirefoxOptions()
            # Descomenta la siguiente línea para ejecutar en modo headless
            # firefox_options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=firefox_options)

        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

    def get_driver(self) -> Optional[webdriver.Remote]:
        """
        Retorna la instancia del driver.

        Returns:
            Optional[webdriver.Remote]: La instancia del driver o None si no está inicializado
        """
        return self.driver

    def go_to_url(self, url: str) -> None:
        """
        Navega a la URL especificada.

        Args:
            url (str): URL de destino

        Raises:
            RuntimeError: Si el driver no está inicializado
        """
        if self.driver is None:
            raise RuntimeError("Driver is not initialized")
        self.driver.get(url)

    def maximize_window(self) -> None:
        """
        Maximiza la ventana del navegador.

        Raises:
            RuntimeError: Si el driver no está inicializado
        """
        if self.driver is None:
            raise RuntimeError("Driver is not initialized")
        self.driver.maximize_window()

    def close(self) -> None:
        """
        Cierra el driver y limpia los recursos.
        """
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    def close_driver(self) -> None:
        """
        Alias para el método close() para mantener compatibilidad.
        """
        self.close()

    def __del__(self):
        """
        Destructor que asegura que el driver se cierre correctamente.
        """
        self.close()
