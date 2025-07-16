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
        cls._go_to_ingredients_page()

    @classmethod
    def teardown_class(cls):
        """Cleanup que se ejecuta al final de la clase"""
        if hasattr(cls, "driver"):
            cls.driver.quit()

    @classmethod
    def _login(cls):
        """Método privado para hacer login"""
        cls.driver.get(f"{settings.BASE_FRONTEND_URL}/login")

        # Esperar a que cargue la página de login y realizar login
        username_input = DepartmentsLocation.LOGIN_EMAIL.wait_until_present(cls.driver)
        password_input = DepartmentsLocation.LOGIN_PASSWORD.find_element(cls.driver)
        login_button = DepartmentsLocation.LOGIN_SUBMIT.find_element(cls.driver)

        username_input.clear()
        username_input.send_keys(settings.ADMIN_USER_EMAIL)
        password_input.clear()
        password_input.send_keys(settings.ADMIN_USER_PASSWORD)
        login_button.click()

        # Esperar a que cargue el dashboard
        DepartmentsLocation.SIDEBAR_TOGGLE.wait_until_present(cls.driver)

    @classmethod
    def _go_to_departmets_page(cls):
        """Navegar a la página de departamentos"""
        menus_dropdown = DepartmentsLocation.NAV_MENUS_TRIGGER.find_element(cls.driver)
        menus_dropdown.click()

        DepartmentsLocation.NAV_INGREDIENTS.wait_until_present(cls.driver)
        ingredients_link = DepartmentsLocation.NAV_INGREDIENTS.find_element(cls.driver)
        ingredients_link.click()

        # Esperar a que cargue la página de departamentos
        DepartmentsLocation.ADD_INGREDIENT_BTN.wait_until_present(cls.driver)

    @add_test_info(
        description="Verificar que la página de departamentos carga correctamente",
        expected_result="La página de departamentos debe cargar sin errores",
        module="Cobertura - UI",
        test_id="DEPARTMENTS-UI-001",
    )
    @pytest.mark.order(1)
    def test_departments_page_loads(self):
        """Verificar que la página de departamentos carga correctamente"""
        # Verificar que la página de departamentos carga correctamente
        page_container = DepartmentsLocation.DEPARTMENTSPAGE.wait_until_present(self.driver)
        assert page_container.is_displayed(), "La página de departamentos no se cargó correctamente"

        # Verificar que el título de la página es correcto
        title = DepartmentsLocation.DEPARTMENTS_TITLE.find_element(self.driver)
        assert "Departamentos" in title.text, "El título de la página no es correcto"

        # Verficar botón de añadir departamento
        add_department_btn = DepartmentsLocation.ADD_DEPARTMENT_BTN.find_element(self.driver)
        assert add_department_btn.is_displayed(), "El botón de añadir departamento no se muestra en la página"
    
    @add_test_info(
        description="Verificar que el botón de añadir departamento funciona correctamente",
        expected_result="El botón de añadir departamento debe abrir el modal de creación",
        module="Cobertura - UI",
        test_id="DEPARTMENTS-UI-002",
    )
    @pytest.mark.order(2)
    def test_add_departamento_button(self):
        """Verificar que el botón de agregar departamento está visible y funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/admin/departamentos")  # Ajusta la URL si es diferente

        # Verificar que el botón de agregar está presente
        add_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Agregar departamento']"))
        )
        assert add_button.is_displayed(), "El botón de agregar departamento no se muestra"
        add_button.click()

        # Verificar que se abre el modal
        dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«r9»"))  # Ajusta el ID si es dinámico o diferente
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
        name_input.send_keys(f"Test Departamento {self.TIMESTAMP}")
        dane_code_input.send_keys("11")

        # Verificar datos ingresados (opcional)
        assert name_input.get_attribute("value") == f"Test Departamento {self.TIMESTAMP}", "El nombre no se ingresó correctamente"
        assert dane_code_input.get_attribute("value") == "11", "El código DANE no se ingresó correctamente"

        # Guardar
        save_button.click()

        # Esperar a que el modal se cierre (asumiendo que desaparece después de guardar)
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "radix-«r9»"))
        )
        # Verificar toast de éxito
        toast = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//li[@data-type='success' and @data-visible='true']"
            ))
        )
        assert toast.is_displayed(), "No se mostró el toast de éxito tras guardar"
    @add_test_info(
        description="Verificar que el botón de editar departamento funciona correctamente",
        expected_result="El botón de editar departamento debe abrir el modal de edición",
        module="Cobertura - UI",
        test_id="DEPARTMENTS-UI-003",
    )
    @pytest.mark.order(3)
    def test_edit_departamento_button(self):
        """Verificar que se puede editar un departamento correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/admin/departamentos")  # Ajusta si es necesario

        # Buscar y hacer clic en el botón de editar del departamento de prueba
        editar_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//h3[normalize-space()='test departamento']/ancestor::div[contains(@class, 'p-4') and contains(@class, 'shadow-sm')]//div[contains(@class,'justify-end')]//button[2]"
            ))
        )
        assert editar_btn.is_displayed(), "El botón de editar no se muestra para 'test departamento'"
        editar_btn.click()

        # Verificar que se abre el modal de edición
        dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«r9»"))  # Ajustar si el ID es dinámico
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
        nuevo_nombre = f"test departamento editado {self.TIMESTAMP}"
        name_input.send_keys(nuevo_nombre)

        # Verificar el cambio
        assert name_input.get_attribute("value") == nuevo_nombre, "El campo de nombre no se actualizó correctamente"

        save_button.click()

        # Verificar que se cierre el modal
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "radix-«r9»"))
        )

        # Verificar que aparece el toast de éxito
        toast = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//li[@data-type='success' and @data-visible='true']"
            ))
        )
        assert toast.is_displayed(), "No se detectó el toast de éxito tras editar el departamento"
    @add_test_info(
        description="Verificar que el botón de eliminar departamento funciona correctamente",
        expected_result="El botón de eliminar departamento debe abrir el modal de confirmación",
        module="Cobertura - UI",
        test_id="DEPARTMENTS-UI-004",
    )
    @pytest.mark.order(4)
    def test_delete_departamento_button(self):
        """Verificar que se puede eliminar un departamento correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/admin/departamentos")  # Ajusta si es necesario

        # Buscar y hacer clic en el botón de eliminar del departamento editado
        delete_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//h3[normalize-space()='test departamento editado']/ancestor::div[contains(@class, 'p-4') and contains(@class, 'shadow-sm')]//div[contains(@class,'justify-end')]//button[3]"
            ))
        )
        assert delete_button.is_displayed(), "El botón de eliminar no se muestra para 'test departamento editado'"
        delete_button.click()

        # Verificar que se abre el modal de confirmación
        delete_dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«rc»"))  # Ajustar si cambia
        )
        assert delete_dialog.is_displayed(), "El diálogo de eliminar departamento no se muestra"

        # Hacer clic en el botón "Eliminar"
        confirm_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Eliminar']"))
        )
        assert confirm_button.is_displayed(), "El botón de confirmar eliminación no se muestra"
        confirm_button.click()

        # Verificar que el diálogo se cierra
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "radix-«rc»"))
        )

        # Verificar que aparece el toast de éxito
        toast = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//li[@data-type='success' and @data-visible='true']"
            ))
        )
        assert toast.is_displayed(), "No se detectó el toast de éxito tras eliminar el departamento"

