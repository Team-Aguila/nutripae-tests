from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import List, Union, Tuple, Optional
import logging


class BasePage:
    """
    Clase base para todas las páginas de la aplicación.
    Proporciona funcionalidades comunes para interactuar con elementos web,
    incluyendo gestión de sidebar y elementos comunes.
    Usa localizadores tradicionales de Selenium.
    """

    MAX_WAIT_TIME_IN_SECONDS = 10

    def __init__(self, driver: Union[webdriver.Chrome, webdriver.Firefox, WebDriver]):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.MAX_WAIT_TIME_IN_SECONDS)
        self.logger = logging.getLogger(self.__class__.__name__)

    # Localizadores tradicionales
    TOGGLE_SIDEBAR_BTN = (By.CSS_SELECTOR, "#sidebar-toggle-btn")
    SIDEBAR_HOME_LINK = (By.CSS_SELECTOR, "#sidebar-menu li a")
    SIDEBAR_ELEMENTS_LIST = (By.CSS_SELECTOR, "#sidebar-menu li button")

    def find_element(self, locator: Tuple[str, str]) -> Optional[WebElement]:
        """
        Busca un elemento en la página.
        Args:
            locator (Tuple[str, str]): Tupla con el tipo de localizador y su valor
        Returns:
            WebElement o None si no se encuentra
        """
        try:
            return self.wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            self.logger.error(f"Element not found: {locator}")
            return None

    def find_elements(self, locator: Tuple[str, str]) -> List[WebElement]:
        """
        Busca múltiples elementos en la página.
        Args:
            locator (Tuple[str, str]): Tupla con el tipo de localizador y su valor
        Returns:
            Lista de WebElements
        """
        try:
            self.wait.until(EC.presence_of_element_located(locator))
            return self.driver.find_elements(*locator)
        except TimeoutException:
            self.logger.error(f"Elements not found: {locator}")
            return []

    def click_element(self, locator: Tuple[str, str]) -> bool:
        """
        Hace clic en un elemento.
        Args:
            locator (Tuple[str, str]): Tupla con el tipo de localizador y su valor
        Returns:
            bool: True si el clic fue exitoso, False en caso contrario
        """
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
            return True
        except TimeoutException:
            self.logger.error(f"Element not clickable: {locator}")
            return False

    def is_element_displayed(self, locator: Tuple[str, str]) -> bool:
        """
        Verifica si un elemento está visible.
        Args:
            locator (Tuple[str, str]): Tupla con el tipo de localizador y su valor
        Returns:
            bool: True si el elemento está visible, False en caso contrario
        """
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            return element.is_displayed()
        except TimeoutException:
            return False

    def wait_element_visible(self, locator: Tuple[str, str]) -> bool:
        """
        Espera a que un elemento sea visible en la página.
        Args:
            locator (Tuple[str, str]): Tupla con el tipo de localizador y su valor
        Returns:
            bool: True si el elemento se vuelve visible, False en caso contrario
        """
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            self.logger.error(f"Element did not become visible: {locator}")
            return False

    def wait_elements_visible(self, locator_list: List[Tuple[str, str]]) -> bool:
        """
        Espera a que múltiples elementos sean visibles en la página.
        Args:
            locator_list (List[Tuple[str, str]]): Lista de localizadores
        Returns:
            bool: True si todos los elementos se vuelven visibles, False en caso contrario
        """
        try:
            for locator in locator_list:
                if not self.wait_element_visible(locator):
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Error waiting for elements to be visible: {e}")
            return False

    def toggle_sidebar(self) -> bool:
        """
        Hace clic en el botón para mostrar u ocultar el sidebar.
        Returns:
            bool: True si el clic fue exitoso, False en caso contrario
        """
        return self.click_element(self.TOGGLE_SIDEBAR_BTN)

    def is_sidebar_visible(self) -> bool:
        """
        Verifica si el sidebar está visible.
        Returns:
            bool: True si el sidebar está visible, False en caso contrario
        """
        return self.is_element_displayed(self.SIDEBAR_ELEMENTS_LIST)

    def go_to_home(self) -> bool:
        """
        Navega a la página de inicio haciendo clic en el enlace del sidebar.
        Returns:
            bool: True si la navegación fue exitosa, False en caso contrario
        """
        return self.click_element(self.SIDEBAR_HOME_LINK)

    def open_sidebar_element(self, element_name: str) -> bool:
        """
        Abre un elemento del sidebar haciendo clic en su botón.
        Args:
            element_name (str): Nombre del elemento del sidebar a abrir
        Returns:
            bool: True si se abrió exitosamente, False en caso contrario
        """
        try:
            elements = self.find_elements(self.SIDEBAR_ELEMENTS_LIST)

            if not elements:
                self.logger.error("No sidebar elements found")
                return False

            for element in elements:
                if element.text.lower() == element_name.lower():
                    element.click()
                    self.logger.info(
                        f"Clicked sidebar element '{element_name}' successfully"
                    )
                    return True

            # Si llegamos aquí, no se encontró el elemento
            available_elements = [elem.text for elem in elements if elem.text]
            self.logger.error(
                f"Sidebar element '{element_name}' not found. Available elements: {available_elements}"
            )
            return False

        except Exception as e:
            self.logger.error(f"Error opening sidebar element '{element_name}': {e}")
            return False

    def get_sidebar_elements(self) -> List[str]:
        """
        Obtiene la lista de nombres de elementos disponibles en el sidebar.
        Returns:
            List[str]: Lista de nombres de elementos del sidebar
        """
        try:
            elements = self.find_elements(self.SIDEBAR_ELEMENTS_LIST)
            return [elem.text for elem in elements if elem.text.strip()]
        except Exception as e:
            self.logger.error(f"Error getting sidebar elements: {e}")
            return []

    def maximize_window(self) -> None:
        """
        Maximiza la ventana del navegador.
        """
        try:
            self.driver.maximize_window()
            self.logger.info("Browser window maximized")
        except Exception as e:
            self.logger.error(f"Error maximizing window: {e}")

    def get_current_url(self) -> str:
        """
        Obtiene la URL actual de la página.
        Returns:
            str: URL actual
        """
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"Error getting current URL: {e}")
            return ""

    def get_page_title(self) -> str:
        """
        Obtiene el título de la página actual.
        Returns:
            str: Título de la página
        """
        try:
            return self.driver.title
        except Exception as e:
            self.logger.error(f"Error getting page title: {e}")
            return ""

    def wait_for_url_to_contain(self, url_fragment: str, timeout: int = 10) -> bool:
        """
        Espera a que la URL contenga un fragmento específico.
        Args:
            url_fragment (str): Fragmento que debe estar en la URL
            timeout (int): Tiempo máximo de espera en segundos
        Returns:
            bool: True si la URL contiene el fragmento, False en caso contrario
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.url_contains(url_fragment))
            self.logger.info(f"URL now contains: {url_fragment}")
            return True
        except TimeoutException:
            current_url = self.get_current_url()
            self.logger.error(
                f"URL did not contain '{url_fragment}' within {timeout} seconds. Current URL: {current_url}"
            )
            return False

    def is_login_successful(self) -> bool:
        """
        Verifica si el login fue exitoso comprobando indicadores comunes.
        Returns:
            bool: True si el login fue exitoso, False en caso contrario
        """
        try:
            # Verificar que no estamos más en la página de login
            current_url = self.get_current_url()
            if "login" in current_url.lower():
                return False

            # Verificar que el sidebar o elementos post-login están presentes
            if self.is_element_displayed(self.TOGGLE_SIDEBAR_BTN):
                self.logger.info("Login successful - sidebar toggle button found")
                return True

            # Verificar otros indicadores de login exitoso
            logout_indicators = [
                (By.CSS_SELECTOR, "[data-testid='logout-button']"),
                (By.CSS_SELECTOR, ".logout-btn"),
                (By.CSS_SELECTOR, "#logout"),
                (By.CSS_SELECTOR, "button[title*='logout']"),
                (By.CSS_SELECTOR, "a[href*='logout']"),
            ]

            for indicator in logout_indicators:
                if self.is_element_displayed(indicator):
                    self.logger.info("Login successful - logout indicator found")
                    return True

            # Si llegamos aquí, probablemente el login fue exitoso pero no encontramos indicadores específicos
            self.logger.warning(
                "Could not find specific login success indicators, but not on login page"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error checking login success: {e}")
            return False
