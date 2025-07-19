"""
Shared pytest fixtures for UI integration tests
"""

import pytest
import logging
import time
from typing import Generator

# Importaciones locales usando relative imports
from .BaseTest import BaseTest
from ..pages.LoginPage import LoginPage
from ..pages.BasePage import BasePage

# Importar settings usando absolute import
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.config import settings


@pytest.fixture(scope="function")
def ui_driver() -> Generator[BaseTest, None, None]:
    """
    Fixture que proporciona un driver configurado para UI tests
    """
    logger = logging.getLogger("ui_driver_fixture")
    logger.info("Setting up UI driver")

    base_test = BaseTest()

    try:
        # Configurar el driver y navegar a la página inicial
        base_test.setup_driver(browser="chrome", url=settings.BASE_FRONTEND_URL)
        logger.info(f"UI driver configured, navigated to: {settings.BASE_FRONTEND_URL}")

        yield base_test

    finally:
        # Cleanup
        logger.info("Tearing down UI driver")
        try:
            base_test.close_driver()
        except Exception as e:
            logger.warning(f"Error during driver cleanup: {e}")


@pytest.fixture(scope="function")
def login_page(ui_driver: BaseTest) -> LoginPage:
    """
    Fixture que proporciona una página de login lista para usar
    """
    logger = logging.getLogger("login_page_fixture")
    logger.info("Loading login page")

    login_page = ui_driver.load_first_page()
    assert login_page is not None, "Login page could not be loaded"
    assert login_page.is_form_displayed(), "Login form is not displayed"

    logger.info("Login page loaded successfully")
    return login_page


@pytest.fixture(scope="function")
def logged_in_base_page(login_page: LoginPage, ui_driver: BaseTest) -> BasePage:
    """
    Fixture que proporciona una BasePage con usuario ya logueado
    """
    logger = logging.getLogger("logged_in_base_page_fixture")
    logger.info("Performing login for fixture")

    # Credenciales por defecto
    email = "admin@test.com"
    password = "Password123!"

    # Realizar login
    login_success = login_page.perform_login(email, password)
    assert login_success, f"Login failed for user: {email}"

    # Esperar procesamiento
    time.sleep(2)

    # Crear BasePage
    if ui_driver.driver_manager is None:
        raise RuntimeError("Driver manager is None after login")

    driver = ui_driver.driver_manager.get_driver()
    assert driver is not None, "Driver is None after login"

    base_page = BasePage(driver)
    base_page.maximize_window()

    # Verificar login exitoso
    assert base_page.is_login_successful(), "Login verification failed"

    logger.info("Login successful, BasePage ready")
    return base_page
