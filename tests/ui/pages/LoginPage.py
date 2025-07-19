import logging
from tests.ui.pages.BasePage import BasePage
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from typing import Union


class LoginPage(BasePage):
    """
    Página de inicio de sesión de la aplicación.
    Proporciona funcionalidades para iniciar sesión y verificar el estado del formulario.
    """

    def __init__(self, driver: Union[webdriver.Chrome, webdriver.Firefox, WebDriver]):
        super().__init__(driver)
        self.logger = logging.getLogger(self.__class__.__name__)

    # Localizadores de elementos
    EMAIL_INPUT = (By.CSS_SELECTOR, "#email")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "#login-button")

    def is_form_displayed(self) -> bool:
        """
        Verifica si el formulario de inicio de sesión está visible.
        Returns:
            bool: True si el formulario está visible, False en caso contrario
        """
        return (
            self.is_element_displayed(self.EMAIL_INPUT)
            and self.is_element_displayed(self.PASSWORD_INPUT)
            and self.is_element_displayed(self.LOGIN_BUTTON)
        )

    def enter_email(self, email: str) -> bool:
        """
        Introduce el email en el campo correspondiente.
        Args:
            email (str): Email a introducir
        Returns:
            bool: True si se introdujo correctamente, False en caso contrario
        """
        try:
            element = self.find_element(self.EMAIL_INPUT)
            if element:
                element.clear()
                element.send_keys(email)
                self.logger.info(f"Email entered successfully: {email}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error entering email: {e}")
            return False

    def enter_password(self, password: str) -> bool:
        """
        Introduce la contraseña en el campo correspondiente.
        Args:
            password (str): Contraseña a introducir
        Returns:
            bool: True si se introdujo correctamente, False en caso contrario
        """
        try:
            element = self.find_element(self.PASSWORD_INPUT)
            if element:
                element.clear()
                element.send_keys(password)
                self.logger.info("Password entered successfully")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error entering password: {e}")
            return False

    def click_login_button(self) -> bool:
        """
        Hace clic en el botón de login.
        Returns:
            bool: True si se hizo clic correctamente, False en caso contrario
        """
        try:
            success = self.click_element(self.LOGIN_BUTTON)
            if success:
                self.logger.info("Login button clicked successfully")
            return success
        except Exception as e:
            self.logger.error(f"Error clicking login button: {e}")
            return False

    def perform_login(self, email: str, password: str) -> bool:
        """
        Realiza el proceso completo de login.
        Args:
            email (str): Email del usuario
            password (str): Contraseña del usuario
        Returns:
            bool: True si el login fue exitoso, False en caso contrario
        """
        try:
            self.logger.info(f"Starting login process for user: {email}")

            if not self.is_form_displayed():
                self.logger.error("Login form is not displayed")
                return False

            if not self.enter_email(email):
                self.logger.error("Failed to enter email")
                return False

            if not self.enter_password(password):
                self.logger.error("Failed to enter password")
                return False

            if not self.click_login_button():
                self.logger.error("Failed to click login button")
                return False

            self.logger.info("Login process completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error during login process: {e}")
            return False
