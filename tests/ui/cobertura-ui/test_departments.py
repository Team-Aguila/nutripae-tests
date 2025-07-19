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


class DepartmentsLocation(Enum):
    """Enum de locators para elementos de la página de departamentos."""

    # Login page
    LOGIN_EMAIL = (By.CSS_SELECTOR, "[name='email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "[name='password']")
    LOGIN_SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    # Navigation
    SIDEBAR_TOGGLE = (By.CSS_SELECTOR, "#sidebar-toggle-btn")
    NAV_COBERTURA_TRIGGER = (By.CSS_SELECTOR, "#nav-coverage-section-trigger")
    NAV_DEPARTMENTS = (By.CSS_SELECTOR, "#nav-departments")

    # Main page
    DEPARTMENTSPAGE = (By.CSS_SELECTOR, "#departments-page")
    DEPARTMENTS_TITLE = (By.CSS_SELECTOR, "#departments-title")
    ADD_DEPARTMENT_BTN = (By.CSS_SELECTOR, "#add-department-btn")
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



class TestDepartmentsUI:
    """Suite de pruebas de UI para Departamentos"""

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
        cls._go_to_departments_page()

    @classmethod
    def teardown_class(cls):
        """Cleanup que se ejecuta al final de la clase"""
        if hasattr(cls, "driver"):
            cls.driver.quit()

    @classmethod
    def _login(cls):
        cls.driver.get(f"{settings.BASE_FRONTEND_URL}/login")

        username_input = DepartmentsLocation.LOGIN_EMAIL.wait_until_present(cls.driver)
        password_input = DepartmentsLocation.LOGIN_PASSWORD.find_element(cls.driver)
        login_button = DepartmentsLocation.LOGIN_SUBMIT.find_element(cls.driver)

        username_input.clear()
        username_input.send_keys(settings.ADMIN_USER_EMAIL)
        password_input.clear()
        password_input.send_keys(settings.ADMIN_USER_PASSWORD)
        login_button.click()

        # Confirmar que se haya redireccionado correctamente
        DepartmentsLocation.SIDEBAR_TOGGLE.wait_until_present(cls.driver)


    @classmethod
    def _go_to_departments_page(cls):
        """Navega a la sección de Departamentos dentro de Cobertura"""
        btn_cobertura = cls.driver.find_element(By.XPATH, "//button[.//span[text()='Cobertura']]")
        btn_cobertura.click()

        departamentos_link = cls.driver.find_element(By.XPATH, "//a[.//span[text()='Departamentos']]")
        departamentos_link.click()

    @add_test_info(
        description="Verificar que la página de departamentos carga correctamente",
        expected_result="La página de departamentos debe cargar sin errores",
        module="Cobertura - UI",
        test_id="DEPARTMENTS-UI-001",
    )
    @pytest.mark.order(75)
    def test_departments_page_loads(self):
        """Verificar que la página de departamentos carga correctamente"""
        # Verificar que el título de la página es correcto
        title = self.driver.find_element(By.XPATH, "//h2[text()='Departamentos']")
        assert "Departamentos" in title.text, "El título de la página no es correcto"
        # Verficar botón de añadir departamento
        add_department_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Agregar departamento')]")
        assert add_department_btn.is_displayed(), "El botón de añadir departamento no se muestra en la página"

    @add_test_info(
        description="Verificar que el botón de añadir departamento funciona correctamente",
        expected_result="El botón de añadir departamento debe abrir el modal de creación",
        module="Cobertura - UI",
        test_id="DEPARTMENTS-UI-002",
    )
    @pytest.mark.order(76)
    def test_add_departamento_button(self):
        """Verificar que el botón de agregar departamento está visible y funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/departments")  # Ajusta la URL si es diferente

        # Verificar que el botón de agregar está presente
        add_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Agregar departamento']"))
        )
        assert add_button.is_displayed(), "El botón de agregar departamento no se muestra"
        add_button.click()

        # Verificar que se abre el modal
        dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«rb»"))  # Ajusta el ID si es dinámico o diferente
        )
        assert dialog.is_displayed(), "El diálogo de creación de departamento no se muestra"

        # Llenar el formulario
        name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "name"))
        )
        dane_code_input = self.driver.find_element(By.ID, "dane_code")
        save_button = self.driver.find_element(By.XPATH, "//button[normalize-space()='Guardar']")

        assert name_input.is_displayed(), "El campo de nombre no se muestra"
        assert dane_code_input.is_displayed(), "El campo DANE no se muestra"
        assert save_button.is_displayed(), "El botón de guardar no se muestra"

        # Ingresar datos
        name_input.send_keys(f"Test Departamento")
        dane_code_input.send_keys("11")

        # Verificar datos ingresados (opcional)
        assert name_input.get_attribute("value") == f"Test Departamento", "El nombre no se ingresó correctamente"
        assert dane_code_input.get_attribute("value") == "11", "El código DANE no se ingresó correctamente"

        # Guardar
        save_button.click()
    @add_test_info(
        description="Verificar que el botón de editar departamento funciona correctamente",
        expected_result="El botón de editar departamento debe abrir el modal de edición",
        module="Cobertura - UI",
        test_id="DEPARTMENTS-UI-003",
        )
    @pytest.mark.order(77)
    def test_edit_departamento_button(self):
        """Verificar que se puede editar un departamento correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/departments")  # Ajusta si es necesario

        # Buscar y hacer clic en el botón de editar del departamento de prueba
        editar_btn = self.driver.find_element(
            By.XPATH,
            "//h3[normalize-space()='Test Departamento']/ancestor::div[contains(@class, 'p-4') and contains(@class, 'shadow-sm')]//div[contains(@class,'justify-end')]//button[2]"
        )
        assert editar_btn.is_displayed(), "El botón de editar no se muestra para 'test departamento'"
        editar_btn.click()

        # Verificar que se abre el modal de edición
        dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«rb»"))  # Ajustar si el ID es dinámico
        )
        assert dialog.is_displayed(), "El diálogo de edición de departamento no se muestra"

        # Editar los datos
        name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "name"))
        )
        save_button = self.driver.find_element(By.XPATH, "//button[normalize-space()='Guardar']")

        assert name_input.is_displayed(), "El campo de nombre no se muestra"
        assert save_button.is_displayed(), "El botón de guardar no se muestra"

        name_input.clear()
        nuevo_nombre = f"test departamento editado"
        name_input.send_keys(nuevo_nombre)

        # Verificar el cambio
        assert name_input.get_attribute("value") == nuevo_nombre, "El campo de nombre no se actualizó correctamente"

        save_button.click()

        # Verificar que se cierre el modal
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "radix-«rb»"))
        )

    @add_test_info(
        description="Verificar que el botón de eliminar departamento funciona correctamente",
        expected_result="El botón de eliminar departamento debe abrir el modal de confirmación",
        module="Cobertura - UI",
        test_id="DEPARTMENTS-UI-004",
    )
    @pytest.mark.order(78)
    def test_delete_departamento_button(self):
        """Verificar que se puede eliminar un departamento correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/departments")  # Ajusta si es necesario
        # Buscar y hacer clic en el botón de eliminar del departamento editado
        delete_button = self.driver.find_element(
            By.XPATH,
            "//h3[normalize-space()='test departamento editado']/ancestor::div[contains(@class, 'p-4') and contains(@class, 'shadow-sm')]//div[contains(@class,'justify-end')]//button[3]"
        )
        assert delete_button.is_displayed(), "El botón de eliminar no se muestra para 'test departamento editado'"
        delete_button.click()
        # Verificar que se abre el modal de confirmación
        delete_dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«re»"))  # Ajustar si cambia
        )
        assert delete_dialog.is_displayed(), "El diálogo de eliminar departamento no se muestra"

        # Hacer clic en el botón "Eliminar"
        confirm_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "confirm-button"))
        )
        assert confirm_button.is_displayed(), "El botón de confirmar eliminación no se muestra"
        confirm_button.click()

        # Verificar que el diálogo se cierra
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "radix-«re»"))
        )