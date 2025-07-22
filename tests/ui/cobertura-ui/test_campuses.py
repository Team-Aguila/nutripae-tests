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

DEFAULT_TIMEOUT = 20  # Tiempo por defecto para esperas


class CampusesLocation(Enum):
    """Enum de locators para elementos de la página de Sedes."""

    # Login page
    LOGIN_EMAIL = (By.CSS_SELECTOR, "[name='email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "[name='password']")
    LOGIN_SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    # Navigation
    SIDEBAR_TOGGLE = (By.CSS_SELECTOR, "#sidebar-toggle-btn")
    NAV_COBERTURA_TRIGGER = (By.CSS_SELECTOR, "#nav-coverage-section-trigger")
    NAV_campuses = (By.CSS_SELECTOR, "#nav-campuses")

    # Main page
    CAMPUSESPAGE = (By.CSS_SELECTOR, "#campuses-page")
    CAMPUSES_TITLE = (By.CSS_SELECTOR, "#campuses-title")
    CAMPUSES_BTN = (By.CSS_SELECTOR, "#add-sedes-btn")

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


class TestCampusesUI:
    """Suite de pruebas de UI para Sedes"""

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
        cls.driver.implicitly_wait(10)
        cls.driver.maximize_window()

        # Hacer login una vez para toda la clase
        cls._login()
        cls._go_to_Campuses_page()

    @classmethod
    def teardown_class(cls):
        """Cleanup que se ejecuta al final de la clase"""
        if hasattr(cls, "driver"):
            cls.driver.quit()

    @classmethod
    def _login(cls):
        cls.driver.get(f"{settings.BASE_FRONTEND_URL}/login")

        username_input = CampusesLocation.LOGIN_EMAIL.wait_until_present(cls.driver)
        password_input = CampusesLocation.LOGIN_PASSWORD.find_element(cls.driver)
        login_button = CampusesLocation.LOGIN_SUBMIT.find_element(cls.driver)

        username_input.clear()
        username_input.send_keys(settings.ADMIN_USER_EMAIL)
        password_input.clear()
        password_input.send_keys(settings.ADMIN_USER_PASSWORD)
        login_button.click()

        # Confirmar que se haya redireccionado correctamente
        CampusesLocation.SIDEBAR_TOGGLE.wait_until_present(cls.driver)

    @classmethod
    def _go_to_Campuses_page(cls):
        """Navega a la sección de Instituciones dentro de Cobertura"""
        btn_cobertura = cls.driver.find_element(
            By.XPATH, "//button[.//span[text()='Cobertura']]"
        )
        btn_cobertura.click()

        departamentos_link = cls.driver.find_element(
            By.XPATH, "//a[.//span[text()='Sedes Educativas']]"
        )
        departamentos_link.click()

    @add_test_info(
        description="Verificar que la página de Sedes carga correctamente",
        expected_result="La página de Sedes debe cargar sin errores",
        module="UI",
        test_id="CAMPUSES-UI-001",
    )
    @pytest.mark.order(87)
    def test_campuses_page_load(self):
        """Verificar que la página de Sedes carga correctamente"""
        # Verificar que el título de la página es correcto
        title = self.driver.find_element(By.XPATH, "//h2[text()='Sedes']")
        assert "Sedes" in title.text, "El título de la página no es correcto"
        # Verficar botón de añadir Institución
        add_department_btn = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Agregar Sede')]"
        )
        assert (
            add_department_btn.is_displayed()
        ), "El botón de añadir Institución no se muestra en la página"

    @add_test_info(
        description="Verificar que el botón de añadir Sedes funciona correctamente",
        expected_result="El botón de añadir Sedes debe abrir el modal de creación",
        module="UI",
        test_id="CAMPUSES-UI-002",
    )
    @pytest.mark.order(88)
    def test_add_campuses_button(self):
        """Verificar que se puede abrir el modal de creación de Sedes"""
        self.driver.get(
            f"{settings.BASE_FRONTEND_URL}/coverage/campuses"
        )  # Ajusta la URL si es diferente
        # Verificar que el botón de agregar está presente
        add_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[normalize-space()='Agregar Sede']")
            )
        )
        assert (
            add_button.is_displayed()
        ), "El botón de agregar Institución no se muestra"
        add_button.click()
        # Verificar que se abre el modal
        dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, "radix-«rb»")
            )  # Ajusta el ID si es dinámico o diferente
        )
        assert (
            dialog.is_displayed()
        ), "El diálogo de creación de institución no se muestra"
        # Llenar el formulario
        name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "name"))
        )
        name.send_keys("test SE")

        dane_code = self.driver.find_element(By.ID, "dane_code")
        dane_code.send_keys("024680")

        address = self.driver.find_element(By.ID, "address")
        address.send_keys("Calle 123 #45-67")

        latitude = self.driver.find_element(By.ID, "latitude")
        latitude.send_keys("3.456789")

        longitude = self.driver.find_element(By.ID, "longitude")
        longitude.send_keys("76.543210")

        # Seleccionar institución educativa asociada
        combo_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']"))
        )
        combo_button.click()

        # Esperar explícitamente que aparezca el contenedor del dropdown
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='listbox']"))
        )

        opcion_ie = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@role='option' and normalize-space()='Angulo-Bolívar']",
                )
            )
        )
        opcion_ie.click()
        save_button = self.driver.find_element(
            By.XPATH, "//button[normalize-space()='Guardar']"
        )
        save_button.click()

    @add_test_info(
        description="Verificar que se puede editar una Sede correctamente",
        expected_result="La Sede debe actualizarse con los nuevos datos",
        module="UI",
        test_id="CAMPUSES-UI-003",
    )
    @pytest.mark.order(89)
    def test_edit_campuses(self):
        """Verificar que se puede editar una Sede correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/campuses")

        # Buscar y hacer clic en el botón de editar del departamento de prueba
        editar_btn = self.driver.find_element(
            By.XPATH,
            "//h3[normalize-space()='test SE']/ancestor::div[contains(@class, 'p-4') and contains(@class, 'shadow-sm')]//div[contains(@class,'justify-end')]//button[2]",
        )
        assert (
            editar_btn.is_displayed()
        ), "El botón de editar no se muestra para 'test SE'"
        editar_btn.click()
        # Verificar que se abre el modal de edición
        dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, "radix-«rb»")
            )  # Ajustar si el ID es dinámico
        )
        assert (
            dialog.is_displayed()
        ), "El diálogo de edición de departamento no se muestra"
        # Editar campos de texto
        name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "name"))
        )
        name.clear()
        name.send_keys("test SE editado")

        address = self.driver.find_element(By.ID, "address")
        address.clear()
        address.send_keys("Calle 765 # 43-21")

        latitude = self.driver.find_element(By.ID, "latitude")
        latitude.clear()
        latitude.send_keys("9.876543")

        longitude = self.driver.find_element(By.ID, "longitude")
        longitude.clear()
        longitude.send_keys("67.12345")

        # Seleccionar institución educativa asociada
        combo_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']"))
        )
        combo_button.click()

        # Esperar explícitamente que aparezca el contenedor del dropdown
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='listbox']"))
        )

        opcion_ie = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='option' and normalize-space()='Castillo Inc']")
            )
        )
        opcion_ie.click()
        save_button = self.driver.find_element(
            By.XPATH, "//button[normalize-space()='Guardar']"
        )
        save_button.click()

    @add_test_info(
        description="Verificar que se puede eliminar una Sede correctamente",
        expected_result="La Sede debe eliminarse y no aparecer en la lista",
        module="UI",
        test_id="CAMPUSES-UI-004",
    )
    @pytest.mark.order(90)
    def test_delete_campuses(self):
        """Verificar que se puede eliminar una Sede correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/campuses")

        # Buscar y hacer clic en el botón de eliminar del departamento de prueba
        eliminar_btn = self.driver.find_element(
            By.XPATH,
            "//h3[normalize-space()='test SE editado']/ancestor::div[contains(@class, 'p-4') and contains(@class, 'shadow-sm')]//div[contains(@class,'justify-end')]//button[3]",
        )
        assert (
            eliminar_btn.is_displayed()
        ), "El botón de eliminar no se muestra para 'test SE editado'"
        eliminar_btn.click()

        # Verificar que se abre el modal de confirmación
        dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, "radix-«re»")
            )  # Ajustar si el ID es dinámico
        )
        assert (
            dialog.is_displayed()
        ), "El diálogo de confirmación de eliminación no se muestra"

        # Confirmar la eliminación
        confirm_button = self.driver.find_element(
            By.XPATH, "//button[normalize-space()='Confirmar']"
        )
        confirm_button.click()
