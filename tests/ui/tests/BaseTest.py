import pytest
import logging
from typing import Optional
from ..utils.DriverManager import DriverManager
from ..pages.LoginPage import LoginPage
from ...config import Settings


class BaseTest:
    """
    Clase base para pruebas de UI que proporciona funcionalidades comunes
    como navegación, manejo del driver y configuración de pruebas.
    """

    def __init__(self):
        self.driver_manager: Optional[DriverManager] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def navigate_to(self, url: str) -> None:
        """
        Navega a la URL especificada. @WARNING: No se recomeienda usar este método fuera del setup
        de pruebas, en su lugar, es mejor manejar el flujo usando las páginas específicas.
        Args:
            url (str): La URL a la que navegar
        Raises:
            ValueError: Si la URL está vacía o es None
            RuntimeError: Si el driver no está inicializado
        """
        if not url or url.strip() == "":
            raise ValueError("BaseTest - navigate_to: The url string is empty!")

        if self.driver_manager is None:
            raise RuntimeError(
                "BaseTest - navigate_to: Driver manager is not initialized"
            )

        self.driver_manager.go_to_url(url)
        self.logger.info(f"Navigated to URL: {url}")

    def load_first_page(self) -> Optional[LoginPage]:
        """
        Carga la primera página (LoginPage).
        Returns:
            LoginPage: Instancia de la página de login o None si hay error
        Raises:
            RuntimeError: Si el driver no está inicializado
        """
        if self.driver_manager is None or self.driver_manager.get_driver() is None:
            raise RuntimeError("BaseTest - load_first_page: Invalid driver")

        try:
            driver = self.driver_manager.get_driver()
            if driver is None:
                return None
            return LoginPage(driver)
        except ImportError:
            self.logger.warning("LoginPage not found, returning None")
            return None

    def setup_driver(
        self, browser: Optional[str] = None, url: Optional[str] = None
    ) -> None:
        """
        Configura el driver del navegador y navega a la URL inicial.

        Args:
            browser (Optional[str]): Nombre del navegador (chrome, firefox)
            url (Optional[str]): URL inicial

        Raises:
            ValueError: Si los parámetros son None o la URL está vacía
        """
        # Cargar propiedades de configuración si existe
        try:
            # Intentar cargar configuración del proyecto

            if browser is None:
                browser = "chrome"
            if url is None or url.strip() == "":
                url = Settings.BASE_FRONTEND_URL

            self.driver_manager = DriverManager(browser)
            self.maximize_window()
            self.navigate_to(url)
            self.logger.info("Configuration loaded successfully")
        except ImportError:
            self.logger.info("No configuration loader found")

        self.logger.info(f"Driver setup completed for browser: {browser}")

    def maximize_window(self) -> None:
        """Maximiza la ventana del navegador."""
        if self.driver_manager and self.driver_manager.get_driver():
            self.driver_manager.maximize_window()

    def close_driver(self) -> None:
        """Cierra el driver del navegador."""
        if self.driver_manager:
            self.driver_manager.close_driver()
            self.driver_manager = None
            self.logger.info("Driver closed successfully")

    # Métodos de pytest fixtures
    @pytest.fixture(scope="session", autouse=True)
    def setup_test(self):
        self.logger.info(f"Starting UI test")
        login_page = self.load_first_page()

        assert login_page is not None, "Login page could not be loaded"
        assert login_page.is_form_displayed(), "Login form is not displayed"

        yield

        self.logger.info(f"Finished all UI tests")
        if hasattr(self, "driver_manager") and self.driver_manager:
            self.close_driver()
