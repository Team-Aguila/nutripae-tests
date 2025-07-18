import pytest  # type: ignore
from datetime import datetime, timezone as tz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from tests.config import settings
from tests.test_metadata import add_test_info

from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEFAULT_TIMEOUT = 3  # Tiempo por defecto para esperas

class CoveragesLocation(Enum):
    """"Enum para las ubicaciones de los coberturas."""
    # Login page
    LOGIN_EMAIL = (By.CSS_SELECTOR, "[name='email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "[name='password']")
    LOGIN_SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    # Navigation
    SIDEBAR_TOGGLE = (By.CSS_SELECTOR, "#sidebar-toggle-btn")
    NAV_COBERTURA_TRIGGER = (By.CSS_SELECTOR, "#nav-coverage-section-trigger")
    NAV_COVERAGES = (By.CSS_SELECTOR, "#nav-coverages")

    # Main page
    COVERAGESPAGE = (By.CSS_SELECTOR, "#coverages-page")
    COVERAGES_TITLE = (By.CSS_SELECTOR, "#coverages-title")
    COVERAGES_BTN = (By.CSS_SELECTOR, "#add-sedes-btn")
    @property
    def by(self):
        return self.value[0]

    @property
    def selector(self):
        return self.value[1]

    def find_element(self, driver):
        return driver.find_element(self.by, self.selector)

    def wait_until_present(self, driver, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((self.by, self.selector))
        )
    
class TestCoveragesUI:
    """Clase para pruebas de la página de coberturas."""

    driver: webdriver.Chrome
    TIMESTAMP = datetime.now(tz.utc).strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def setup_class(cls):
        """Setup que se ejecuta una vez al inicio de la clase - configura driver y login"""
        # Configurar Chrome
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        # chrome_options.add_argument("--headless")  # Para debugging

        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.delete_all_cookies()  # Limpiar cookies antes de cada prueba
        cls.driver.implicitly_wait(5)
        cls.driver.maximize_window()

        # Hacer login una vez para toda la clase
        cls._login()
        cls._go_to_Coverages_page()
    @classmethod
    def _login(cls):
        cls.driver.get(f"{settings.BASE_FRONTEND_URL}/login")

        username_input = CoveragesLocation.LOGIN_EMAIL.wait_until_present(cls.driver)
        password_input = CoveragesLocation.LOGIN_PASSWORD.find_element(cls.driver)
        login_button = CoveragesLocation.LOGIN_SUBMIT.find_element(cls.driver)

        username_input.clear()
        username_input.send_keys(settings.ADMIN_USER_EMAIL)
        password_input.clear()
        password_input.send_keys(settings.ADMIN_USER_PASSWORD)
        login_button.click()
        # Confirmar que se haya redireccionado correctamente
        CoveragesLocation.SIDEBAR_TOGGLE.wait_until_present(cls.driver)

    @classmethod
    def _go_to_Coverages_page(cls):
        """Navega a la sección de Instituciones dentro de Cobertura"""
        btn_cobertura = cls.driver.find_element(By.XPATH, "//button[.//span[text()='Cobertura']]")
        btn_cobertura.click()

        cobertura_link = cls.driver.find_element(By.XPATH, "//a[.//span[text()='Cobertura']]")
        cobertura_link.click()


    @add_test_info(
        description="Verificar que la página de Coberturas carga correctamente",
        expected_result="La página de Coberturas debe cargar sin errores",
        module="Cobertura - UI",
        test_id="COVERAGES-UI-001",
    )
    def test_coberturas_page_load(self):
        """Verificar que la página de Coberturas carga correctamente"""
        # Verificar que el título de la página es correcto
        title = self.driver.find_element(By.XPATH, "//h2[normalize-space()='Coberturas']")
        assert "Coberturas" in title.text, "El título de la página no es correcto"
        # Verficar botón de añadir cobertura
        add_coverages_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Agregar Cobertura')]")
        assert add_coverages_btn.is_displayed(), "El botón de añadir Institución no se muestra en la página"

    @add_test_info(
        description="Verificar que el botón de añadir Coberturas funciona correctamente",
        expected_result="El botón de añadir Coberturas debe abrir el modal de creación",
        module="Cobertura - UI",
        test_id="COVERAGES-UI-002",
    )
    def test_add_coverages_button(self):
        """Verificar que el botón de añadir Coberturas funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/coverages")  # Ajusta la URL si es diferente
        # Verificar que el botón de agregar está presente
        add_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Agregar Cobertura']"))
        )
        assert add_button.is_displayed(), "El botón de agregar Institución no se muestra"
        add_button.click()
        # Verificar que se abre el modal
        dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«rb»"))  # Ajusta el ID si es dinámico o diferente
        )
        assert dialog.is_displayed(), "El diálogo de creación de coberturas no se muestra"
        combo_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Seleccione un beneficiario']]"))
        )
        combo_button.click()
        option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and normalize-space(.)='Pablo Moreno']"))
        )
        assert option.is_displayed(), "La opción de beneficiario no se muestra"
        option.click()
        sede_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Seleccione una sede']]"))
        )
        sede_button.click()
        option_sede = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and normalize-space(.)='Sede Arias']"))
        )
        assert option_sede.is_displayed(), "La opción de beneficiario no se muestra"
        option_sede.click()

        beneficio_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Seleccione un tipo']]"))
        )
        beneficio_button.click()
        option_beneficio = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and normalize-space(.)='desayuno']"))
        )
        assert option_beneficio.is_displayed(), "La opción de beneficiario no se muestra"
        option_beneficio.click()
        guardar_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Guardar']"))
        )
        assert guardar_button.is_displayed(), "El botón de guardar no se muestra en el modal"
        guardar_button.click()