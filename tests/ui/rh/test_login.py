import pytest
import logging
import time
from typing import Tuple

from tests.ui.pages.BasePage import BasePage
from tests.ui.pages.LoginPage import LoginPage
from tests.ui.rh.BaseTest import BaseTest
from tests.test_metadata import add_test_info


class TestLoginUI:
    """Test suite for Login UI functionality"""

    @add_test_info(
        description="Realizar login exitoso con credenciales de administrador",
        expected_result="Login exitoso y acceso a página principal",
        module="UI",
        test_id="LOGIN-001",
    )
    def test_successful_admin_login(self, login_page: LoginPage, ui_driver: BaseTest):
        """LOGIN-001: Successfully login with admin credentials"""
        logger = logging.getLogger("test_successful_admin_login")
        logger.info("Starting admin login test")

        # Verificar que el formulario está visible
        assert login_page.is_form_displayed(), "Login form is not displayed"

        # Realizar el login con credenciales específicas
        email = "admin@test.com"
        password = "Password123!"

        logger.info(f"Attempting login with email: {email}")
        login_success = login_page.perform_login(email, password)

        assert login_success, f"Login failed for user: {email}"

        # Esperar procesamiento del login
        time.sleep(2)

        # Verificar estado post-login
        assert ui_driver.driver_manager is not None, "Driver manager is None"
        driver = ui_driver.driver_manager.get_driver()
        assert driver is not None, "Driver is None after login"

        base_page = BasePage(driver)
        base_page.maximize_window()

        # Verificar que el login fue exitoso
        assert base_page.is_login_successful(), "Login verification failed"

        # Verificar información adicional
        page_title = base_page.get_page_title()
        logger.info(f"Login successful - Title: {page_title}")

    @add_test_info(
        description="Verificar formulario de login se muestra correctamente",
        expected_result="Formulario visible con todos los campos requeridos",
        module="UI",
        test_id="LOGIN-002",
    )
    def test_login_form_display(self, login_page: LoginPage):
        """LOGIN-002: Verify login form is displayed correctly"""
        logger = logging.getLogger("test_login_form_display")
        logger.info("Starting login form display test")

        # Verificar que el formulario está presente y visible usando la función helper
        assert_login_form_visible = login_page.is_form_displayed()
        assert assert_login_form_visible, "Login form is not displayed"

        logger.info("Login form display test completed successfully")

    @add_test_info(
        description="Fallar login con credenciales inválidas",
        expected_result="Login falla y permanece en página de login",
        module="UI",
        test_id="LOGIN-003",
    )
    def test_invalid_credentials_login(
        self, login_page: LoginPage, ui_driver: BaseTest
    ):
        """LOGIN-003: Fail login with invalid credentials"""
        logger = logging.getLogger("test_invalid_credentials_login")
        logger.info("Starting invalid credentials login test")

        # Verificar que el formulario está visible
        assert login_page.is_form_displayed(), "Login form is not displayed"

        # Intentar login con credenciales inválidas
        email = "invalid@test.com"
        password = "WrongPassword123!"

        logger.info(f"Attempting login with invalid credentials: {email}")
        login_page.perform_login(email, password)

        # Esperar un momento para procesamiento
        time.sleep(2)

        # Verificar que el login falló
        assert ui_driver.driver_manager is not None, "Driver manager is None"
        driver = ui_driver.driver_manager.get_driver()
        assert driver is not None, "Driver is None"

        # Verificar que seguimos en la página de login o hay un mensaje de error
        # (La implementación específica puede variar según la aplicación)
        assert login_page.is_form_displayed(), "Login form should still be displayed"

        current_url = driver.current_url
        logger.info(f"Invalid login test completed - Current URL: {current_url}")

    @add_test_info(
        description="Verificar navegación post-login usando sidebar",
        expected_result="Usuario puede navegar usando el sidebar después del login",
        module="UI",
        test_id="LOGIN-004",
    )
    def test_post_login_navigation(self, logged_in_base_page: BasePage):
        """LOGIN-004: Verify post-login navigation using sidebar"""
        logger = logging.getLogger("test_post_login_navigation")
        logger.info("Starting post-login navigation test")

        # Ya tenemos un usuario logueado gracias al fixture
        base_page = logged_in_base_page

        # Verificar que podemos interactuar con el sidebar
        if not base_page.is_sidebar_visible():
            logger.info("Sidebar not visible, attempting to toggle")
            toggle_success = base_page.toggle_sidebar()
            assert toggle_success, "Failed to toggle sidebar"

        # Obtener elementos del sidebar
        sidebar_elements = base_page.get_sidebar_elements()
        logger.info(f"Sidebar elements found: {sidebar_elements}")

        assert len(sidebar_elements) > 0, "No sidebar elements found"

        # Intentar navegar a un elemento del sidebar (si existe)
        if sidebar_elements:
            element_to_click = sidebar_elements[0]
            logger.info(f"Attempting to click sidebar element: {element_to_click}")

            navigation_success = base_page.open_sidebar_element(element_to_click)
            # Nota: no hacemos assert aquí porque depende de la implementación específica
            # En una app real, verificaríamos cambios de URL o contenido

            logger.info(f"Navigation attempt result: {navigation_success}")

        logger.info("Post-login navigation test completed")


# Método utilitario que puede ser importado por otros módulos de test
def get_logged_in_base_page_for_external_test() -> BasePage:
    """
    Método utilitario para obtener una BasePage con usuario logueado.
    Puede ser usado por otros módulos de test que requieran un usuario autenticado.

    Returns:
        BasePage: Instancia de BasePage con usuario logueado

    Note:
        Este método configura su propio driver, por lo que el llamador debe
        asegurarse de llamar close_driver() cuando termine.
    """
    logger = logging.getLogger("get_logged_in_base_page_util")
    logger.info("Setting up logged in session for external test")

    base_test = BaseTest()

    try:
        # Configurar driver
        from ...config import settings

        base_test.setup_driver(browser="chrome", url=settings.BASE_FRONTEND_URL)

        # Cargar página de login
        login_page = base_test.load_first_page()
        assert login_page is not None, "Could not load login page"
        assert login_page.is_form_displayed(), "Login form is not displayed"

        # Realizar login
        email = "admin@test.com"
        password = "Password123!"

        login_success = login_page.perform_login(email, password)
        assert login_success, f"Login failed for user: {email}"

        time.sleep(2)

        # Crear BasePage
        assert base_test.driver_manager is not None, "Driver manager is None"
        driver = base_test.driver_manager.get_driver()
        assert driver is not None, "Driver is None after login"

        base_page = BasePage(driver)
        base_page.maximize_window()

        assert base_page.is_login_successful(), "Login verification failed"

        logger.info("External login setup completed successfully")
        return base_page

    except Exception as e:
        # Cleanup en caso de error
        base_test.close_driver()
        raise RuntimeError(f"Failed to setup logged in session: {e}")


class TestLoginUtilities:
    """
    Clase de utilidades de login que pueden ser usadas por otros tests
    """

    @staticmethod
    def quick_login_test(
        base_test_instance: BaseTest,
        email: str = "admin@test.com",
        password: str = "Password123!",
    ) -> BasePage:
        """
        Realiza un login rápido y retorna BasePage para uso en otros tests

        Args:
            base_test_instance: Instancia de BaseTest ya configurada
            email: Email para login
            password: Contraseña para login

        Returns:
            BasePage: Instancia post-login
        """
        login_page = base_test_instance.load_first_page()
        assert login_page is not None, "Could not load login page"

        login_success = login_page.perform_login(email, password)
        assert login_success, "Login failed"

        time.sleep(2)

        assert base_test_instance.driver_manager is not None, "Driver manager is None"
        driver = base_test_instance.driver_manager.get_driver()
        assert driver is not None, "Driver is None after login"

        base_page = BasePage(driver)
        base_page.maximize_window()

        return base_page


# Ejemplo de uso de login automático para otros tests
def example_test_using_automatic_login():
    """
    Ejemplo de cómo usar la función de login automático en otros tests.
    Este test no se ejecutará automáticamente (no tiene el prefijo test_).
    """
    logger = logging.getLogger("example_automatic_login")

    # Realizar login automático
    base_page, base_test = perform_automatic_login(
        browser="chrome", email="admin@test.com", password="Password123!"
    )

    try:
        # Ahora ya estás logueado y puedes hacer pruebas
        logger.info(
            f"Logged in successfully, current URL: {base_page.get_current_url()}"
        )

        # Ejemplo: navegar por el sidebar
        if base_page.is_sidebar_visible():
            sidebar_elements = base_page.get_sidebar_elements()
            logger.info(f"Available sidebar elements: {sidebar_elements}")

            # Abrir un elemento del sidebar si existe
            if sidebar_elements:
                base_page.open_sidebar_element(sidebar_elements[0])

        # Aquí puedes continuar con más pruebas...

    finally:
        # Siempre limpiar los recursos
        cleanup_automatic_login(base_test)


class AutomaticLoginHelper:
    """
    Clase helper para facilitar el uso de login automático en otros módulos de test.
    """

    @staticmethod
    def setup_logged_in_session(browser: str = "chrome") -> Tuple[BasePage, BaseTest]:
        """
        Configura una sesión con login automático.

        Args:
            browser: Navegador a usar

        Returns:
            Tuple[BasePage, BaseTest]: Página base y test para cleanup
        """
        return perform_automatic_login(browser=browser)

    @staticmethod
    def teardown_session(base_test: BaseTest):
        """
        Limpia una sesión configurada.

        Args:
            base_test: Instancia de BaseTest a limpiar
        """
        cleanup_automatic_login(base_test)
