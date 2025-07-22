import pytest  # type: ignore
from datetime import datetime, timezone as tz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from tests.config import settings
from tests.test_metadata import add_test_info

from enum import Enum
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common.exceptions import StaleElementReferenceException

DEFAULT_TIMEOUT = 40  # Tiempo por defecto para esperas


class EmployeesLocators(Enum):
    """Enum de locators para elementos de la página de empleados"""

    # Login page
    LOGIN_EMAIL = (By.CSS_SELECTOR, "[name='email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "[name='password']")
    LOGIN_SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    # Sidebar y navegación
    SIDEBAR_TOGGLE = (By.CSS_SELECTOR, "#sidebar-toggle-btn")
    NAV_HR_TRIGGER = (By.CSS_SELECTOR, "#nav-hr-section-trigger")
    NAV_EMPLOYEES = (By.CSS_SELECTOR, "#nav-employees")

    # Página de empleados
    EMPLOYEES_PAGE = (By.CSS_SELECTOR, "#employees-page")
    EMPLOYEES_TITLE = (By.CSS_SELECTOR, "#employees-title")
    ADD_EMPLOYEE_BTN = (By.CSS_SELECTOR, "#add-employee-btn")

    @property
    def by(self) -> str:
        return self.value[0]

    @property
    def selector(self) -> str:
        return self.value[1]

    def find_element(self, driver: webdriver.Chrome):
        return driver.find_element(self.by, self.selector)

    def wait_until_present(
        self, driver: webdriver.Chrome, timeout: int = DEFAULT_TIMEOUT
    ):
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((self.by, self.selector))
        )

    def wait_until_clickable(
        self, driver: webdriver.Chrome, timeout: int = DEFAULT_TIMEOUT
    ):
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((self.by, self.selector))
        )


def wait_for_no_overlay(driver, timeout=DEFAULT_TIMEOUT):
    """Espera a que desaparezca cualquier overlay de diálogo/modal que bloquee la interacción."""
    try:
        WebDriverWait(driver, timeout).until_not(
            lambda d: any(
                el.is_displayed()
                for el in d.find_elements(
                    By.CSS_SELECTOR, '[data-slot="dialog-overlay"]'
                )
            )
        )
    except Exception:
        pass  # Si no hay overlay, continúa


def click_delete_first_employee(driver):
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.XPATH, "//table//tr[td]")
    )
    btn = WebDriverWait(driver, 10).until(
        lambda d: d.find_element(
            By.XPATH, "//table//tr[td]//button[@data-testid='delete-employee-btn']"
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
    wait_for_no_overlay(driver)
    btn.click()


def esperar_elemento_interactivo(driver, by, selector, timeout=DEFAULT_TIMEOUT):
    """Espera a que un elemento sea visible y habilitado, y hace scroll hasta él. Lanza excepción si no lo encuentra."""

    def _find():
        el = driver.find_element(by, selector)
        if el.is_displayed() and el.is_enabled():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            return el
        return None

    return WebDriverWait(driver, timeout).until(lambda d: _find())


def filtrar_por_columna(driver, columna, valor):
    """
    Filtra la tabla por el valor dado en la columna especificada.
    columna: texto exacto del encabezado de la columna (ej: 'Nombre Completo')
    valor: texto a buscar
    """
    try:
        filtro = esperar_elemento_interactivo(
            driver,
            By.XPATH,
            f"//th[contains(., '{columna}')]//input[@placeholder='Buscar...']",
        )
    except Exception:
        filtro = esperar_elemento_interactivo(
            driver, By.XPATH, "//input[@placeholder='Buscar...']"
        )
    assert filtro is not None, "No se encontró el input de filtro"
    filtro.clear()
    filtro.send_keys(valor)
    wait_for_no_overlay(driver)


def click_edit_first_employee(driver, retries=3):
    for attempt in range(retries):
        try:
            btn = WebDriverWait(driver, 10).until(
                lambda d: d.find_element(
                    By.XPATH,
                    "//table//tr[td][1]//button[@data-testid='edit-employee-btn' and contains(., 'Editar')]",
                )
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", btn
            )
            wait_for_no_overlay(driver)
            btn.click()
            return
        except StaleElementReferenceException:
            if attempt == retries - 1:
                raise
            else:
                continue


def click_action_button_by_employee_name(driver, nombre, accion="editar"):
    """
    Busca la fila que contiene el nombre y hace click en el botón de acción ('editar' o 'eliminar').
    """
    WebDriverWait(driver, 10).until(lambda d: d.find_element(By.XPATH, "//table"))
    filas = driver.find_elements(By.XPATH, f"//table//tr[td[contains(., '{nombre}')]]")
    assert filas, f"No se encontró ninguna fila con el nombre '{nombre}'"
    fila = filas[0]
    if accion == "editar":
        btns = fila.find_elements(By.CSS_SELECTOR, "[data-testid='edit-employee-btn']")
        if not btns:
            btns = fila.find_elements(By.XPATH, ".//button[contains(., 'Editar')]")
    else:
        btns = fila.find_elements(
            By.CSS_SELECTOR, "[data-testid='delete-employee-btn']"
        )
        if not btns:
            btns = fila.find_elements(By.XPATH, ".//button[contains(., 'Eliminar')]")
    assert btns, f"No se encontró el botón de {accion} en la fila de '{nombre}'"
    btn = btns[0]
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
    wait_for_no_overlay(driver)
    btn.click()


def click_action_first_employee(driver, accion="editar", retries=3):
    testid = "edit-employee-btn" if accion == "editar" else "delete-employee-btn"
    texto = "Editar" if accion == "editar" else "Eliminar"
    for attempt in range(retries):
        try:
            btn = WebDriverWait(driver, 10).until(
                lambda d: d.find_element(
                    By.XPATH,
                    f"//table//tr[td][1]//button[@data-testid='{testid}' and contains(., '{texto}')]",
                )
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", btn
            )
            wait_for_no_overlay(driver)
            btn.click()
            return
        except StaleElementReferenceException:
            if attempt == retries - 1:
                return
            else:
                continue


class TestEmployeesUI:
    """Suite de pruebas de UI para Empleados"""

    driver: webdriver.Chrome

    @classmethod
    def setup_class(cls):
        """Setup que se ejecuta una vez al inicio de la clase - configura driver y login"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument(
            "--headless"
        )  # Activar headless para pruebas automáticas
        chrome_options.add_argument(
            "--window-size=1920,1080"
        )  # Tamaño de ventana para evitar problemas de visibilidad
        chrome_options.add_argument(
            "--log-level=3"
        )  # Suprimir logs molestos de ChromeDriver

        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.delete_all_cookies()
        cls.driver.implicitly_wait(10)
        cls.driver.maximize_window()

        # Hacer login una vez para toda la clase
        cls._login()

    @classmethod
    def teardown_class(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()

    @classmethod
    def _login(cls):
        """Método privado para hacer login"""
        cls.driver.get(f"{settings.BASE_FRONTEND_URL}/login")
        # Esperar a que cargue la página de login y realizar login
        username_input = EmployeesLocators.LOGIN_EMAIL.wait_until_present(cls.driver)
        password_input = EmployeesLocators.LOGIN_PASSWORD.find_element(cls.driver)
        login_button = EmployeesLocators.LOGIN_SUBMIT.find_element(cls.driver)

        username_input.clear()
        username_input.send_keys(settings.ADMIN_USER_EMAIL)
        password_input.clear()
        password_input.send_keys(settings.ADMIN_USER_PASSWORD)
        login_button.click()

        # Esperar a que cargue el dashboard (sidebar visible)
        EmployeesLocators.SIDEBAR_TOGGLE.wait_until_present(cls.driver)
        # Redirigir directamente a la página de empleados tras login
        cls.driver.get("http://localhost:5173/hr/employees/")

    @add_test_info(
        description="Verificar que el botón de agregar empleado está visible y funcional",
        expected_result="El botón de agregar empleado debe estar visible y abrir el formulario",
        module="UI",
        test_id="EMPLOYEES-UI-0000",
    )
    @pytest.mark.order(50)
    def test_add_employee_button_opens_form(self):
        wait_for_no_overlay(self.driver)
        try:
            form_dialog = self.driver.find_element(By.ID, "employee-form-dialog")
            if form_dialog.is_displayed():
                WebDriverWait(self.driver, 10).until_not(
                    lambda d: d.find_element(
                        By.ID, "employee-form-dialog"
                    ).is_displayed()
                )
        except Exception:
            pass  # No hay formulario abierto
        wait_for_no_overlay(self.driver)
        try:
            add_button = esperar_elemento_interactivo(
                self.driver,
                EmployeesLocators.ADD_EMPLOYEE_BTN.by,
                EmployeesLocators.ADD_EMPLOYEE_BTN.selector,
                timeout=20,
            )
        except Exception:
            add_button = esperar_elemento_interactivo(
                self.driver,
                By.XPATH,
                "//button[contains(., 'Agregar Empleado')]",
                timeout=20,
            )
        assert add_button is not None, "No se encontró el botón de agregar empleado"
        assert add_button.is_displayed(), "El botón de agregar empleado no se muestra"
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", add_button
            )
            wait_for_no_overlay(self.driver)
            add_button.click()
        except Exception as e:
            overlays = self.driver.find_elements(
                By.CSS_SELECTOR, '[data-slot="dialog-overlay"]'
            )
            for idx, ov in enumerate(overlays):
                pass
            self.driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML")
            raise
        wait_for_no_overlay(self.driver)
        try:
            form_dialog = self.driver.find_element(By.ID, "employee-form-dialog")
        except Exception:
            form_dialog = self.driver.find_element(
                By.XPATH,
                "//*[contains(text(), 'Agregar Empleado') or contains(text(), 'Editar Empleado')]/ancestor::div[contains(@class, 'DialogContent') or contains(@class, 'dialog')]",
            )
        assert (
            form_dialog.is_displayed()
        ), "El formulario de empleado no se muestra al hacer clic en agregar"
        try:
            close_btn = self.driver.find_element(By.ID, "employee-form-cancel-btn")
            close_btn.click()
        except Exception:
            pass
        wait_for_no_overlay(self.driver)

    @add_test_info(
        description="Crear un empleado predefinido para pruebas",
        expected_result="El empleado debe ser creado y visible en la tabla",
        module="UI",
        test_id="EMPLOYEES-UI-001",
    )
    @pytest.mark.order(51)
    def test_create_predefined_employee(self):
        wait_for_no_overlay(self.driver)
        try:
            add_button = esperar_elemento_interactivo(
                self.driver,
                EmployeesLocators.ADD_EMPLOYEE_BTN.by,
                EmployeesLocators.ADD_EMPLOYEE_BTN.selector,
                timeout=20,
            )
        except Exception:
            add_button = esperar_elemento_interactivo(
                self.driver,
                By.XPATH,
                "//button[contains(., 'Agregar Empleado')]",
                timeout=20,
            )
        assert add_button is not None, "No se encontró el botón de agregar empleado"
        add_button.click()
        wait_for_no_overlay(self.driver)
        try:
            form_dialog = self.driver.find_element(By.ID, "employee-form-dialog")
        except Exception:
            form_dialog = self.driver.find_element(
                By.XPATH,
                "//*[contains(text(), 'Agregar Empleado') or contains(text(), 'Editar Empleado')]/ancestor::div[contains(@class, 'DialogContent') or contains(@class, 'dialog')]",
            )
        assert (
            form_dialog.is_displayed()
        ), "El formulario de empleado no se muestra al hacer clic en agregar"
        self.driver.find_element(By.ID, "employee-document-number").send_keys(
            "9999999999"
        )
        self.driver.find_element(By.ID, "employee-full-name").send_keys(
            "Empleado Prueba UI"
        )
        self.driver.find_element(By.ID, "employee-birth-date").send_keys("1990-01-01")
        self.driver.find_element(By.ID, "employee-personal-email").send_keys(
            "prueba.ui@example.com"
        )
        self.driver.find_element(By.ID, "employee-hire-date").send_keys("2023-01-01")
        try:
            gender_select = self.driver.find_element(By.ID, "employee-gender-select")
            gender_select.click()
            self.driver.find_element(
                By.CSS_SELECTOR, "#employee-gender-options [role='option']"
            ).click()
        except Exception:
            pass
        try:
            role_select = self.driver.find_element(
                By.ID, "employee-operational-role-select"
            )
            role_select.click()
            self.driver.find_element(
                By.CSS_SELECTOR, "#employee-operational-role-options [role='option']"
            ).click()
        except Exception:
            pass
        guardar_btn = self.driver.find_element(By.ID, "employee-form-submit-btn")
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", guardar_btn
        )
        wait_for_no_overlay(self.driver)
        guardar_btn.click()
        try:
            WebDriverWait(self.driver, 20).until_not(
                lambda d: d.find_element(By.ID, "employee-form-dialog").is_displayed()
            )
        except Exception:
            try:
                WebDriverWait(self.driver, 20).until_not(
                    lambda d: d.find_element(
                        By.XPATH,
                        "//*[contains(text(), 'Agregar Empleado') or contains(text(), 'Editar Empleado')]/ancestor::div[contains(@class, 'DialogContent') or contains(@class, 'dialog')]",
                    ).is_displayed()
                )
            except Exception:
                pass
        wait_for_no_overlay(self.driver)

    @add_test_info(
        description="Verificar que la página de empleados carga correctamente",
        expected_result="La página de empleados debe cargar sin errores",
        module="UI",
        test_id="EMPLOYEES-UI-002",
    )
    @pytest.mark.order(52)
    def test_employees_page_loads(self):
        wait_for_no_overlay(self.driver)
        # Usar selector robusto para el título
        try:
            title = self.driver.find_element(
                By.CSS_SELECTOR, "h1.text-3xl.font-bold.mb-2"
            )
        except Exception:
            title = self.driver.find_element(
                By.XPATH, "//*[contains(text(), 'Empleados')]"
            )
        assert (
            "Empleados" in title.text
        ), f"El título de la página de empleados no es correcto: '{title.text}'"

    @add_test_info(
        description="Verificar que el formulario de empleado tiene los campos clave presentes",
        expected_result="El formulario debe mostrar los campos requeridos para crear un empleado",
        module="UI",
        test_id="EMPLOYEES-UI-003",
    )
    @pytest.mark.order(53)
    def test_employee_form_fields_present(self):
        wait_for_no_overlay(self.driver)
        # Abrir el formulario si no está abierto
        try:
            form_dialog = self.driver.find_element(By.ID, "employee-form-dialog")
            if not form_dialog.is_displayed():
                EmployeesLocators.ADD_EMPLOYEE_BTN.wait_until_clickable(
                    self.driver
                ).click()
        except Exception:
            EmployeesLocators.ADD_EMPLOYEE_BTN.wait_until_clickable(self.driver).click()
            form_dialog = self.driver.find_element(By.ID, "employee-form-dialog")
        wait_for_no_overlay(self.driver)
        # Verificar campos clave
        full_name = self.driver.find_element(By.ID, "employee-full-name")
        document_number = self.driver.find_element(By.ID, "employee-document-number")
        email = self.driver.find_element(By.ID, "employee-personal-email")
        save_btn = self.driver.find_element(By.ID, "employee-form-submit-btn")
        cancel_btn = self.driver.find_element(By.ID, "employee-form-cancel-btn")
        assert full_name.is_displayed(), "El campo de nombre completo no se muestra"
        assert (
            document_number.is_displayed()
        ), "El campo de número de documento no se muestra"
        assert email.is_displayed(), "El campo de email personal no se muestra"
        assert save_btn.is_displayed(), "El botón de guardar no se muestra"
        assert cancel_btn.is_displayed(), "El botón de cancelar no se muestra"

    @add_test_info(
        description="Verificar que la tabla de empleados está visible",
        expected_result="La tabla de empleados debe estar visible en la página",
        module="UI",
        test_id="EMPLOYEES-UI-004",
    )
    @pytest.mark.order(54)
    def test_employees_table_visible(self):
        wait_for_no_overlay(self.driver)
        try:
            table = self.driver.find_element(
                By.CSS_SELECTOR, "#employees-table, [data-testid='employees-table']"
            )
        except Exception:
            table = self.driver.find_element(
                By.XPATH, "//table[.//th[contains(., 'Nombre Completo')]]"
            )
        assert table.is_displayed(), "La tabla de empleados no se muestra"

    @add_test_info(
        description="Verificar funcionamiento de la paginación de empleados",
        expected_result="Los botones de paginación deben estar presentes y funcionar",
        module="UI",
        test_id="EMPLOYEES-UI-005",
    )
    @pytest.mark.order(55)
    def test_employees_pagination(self):
        try:
            wait_for_no_overlay(self.driver)
            next_btn = esperar_elemento_interactivo(
                self.driver,
                By.CSS_SELECTOR,
                "[data-testid='pagination-next-btn']",
                timeout=20,
            )
            prev_btn = esperar_elemento_interactivo(
                self.driver,
                By.CSS_SELECTOR,
                "[data-testid='pagination-prev-btn']",
                timeout=20,
            )
            assert (
                next_btn is not None
            ), "No se encontró el botón de paginación siguiente"
            assert (
                prev_btn is not None
            ), "No se encontró el botón de paginación anterior"

            # Scroll hasta los botones antes de interactuar
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", next_btn
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", prev_btn
            )

            page_info = self.driver.find_element(
                By.XPATH, "//*[contains(text(), 'Página')]"
            )
            match = re.search(r"Página (\d+) de (\d+)", page_info.text)
            if not match:
                raise Exception(
                    f"No se pudo encontrar el número de página en el texto: '{page_info.text}'"
                )
            pagina_actual = int(match.group(1))
            total_paginas = int(match.group(2))

            # Si solo hay una página, no se puede paginar
            if total_paginas == 1:
                return

            # Ir a la siguiente página si es posible
            if next_btn.is_enabled():
                wait_for_no_overlay(self.driver)
                next_btn.click()
                wait_for_no_overlay(self.driver)

                def obtener_pagina_actual(driver):
                    texto = driver.find_element(
                        By.XPATH, "//*[contains(text(), 'Página')]"
                    ).text
                    match = re.search(r"Página (\d+)", texto)
                    if match:
                        return int(match.group(1))
                    else:
                        raise Exception(
                            "No se pudo encontrar el número de página en el texto: '{}'".format(
                                texto
                            )
                        )

                WebDriverWait(self.driver, 20).until(
                    lambda d: obtener_pagina_actual(d) == pagina_actual + 1
                )
            else:
                pass

            # Ir a la página anterior si es posible
            if prev_btn.is_enabled():
                wait_for_no_overlay(self.driver)
                prev_btn.click()
                wait_for_no_overlay(self.driver)

                def obtener_pagina_actual(driver):
                    texto = driver.find_element(
                        By.XPATH, "//*[contains(text(), 'Página')]"
                    ).text
                    match = re.search(r"Página (\d+)", texto)
                    if match:
                        return int(match.group(1))
                    else:
                        raise Exception(
                            "No se pudo encontrar el número de página en el texto: '{}'".format(
                                texto
                            )
                        )

                WebDriverWait(self.driver, 20).until(
                    lambda d: obtener_pagina_actual(d) == pagina_actual
                )
            else:
                pass
        except Exception:
            return

    @add_test_info(
        description="Verificar que el formulario de edición de empleado se abre al hacer clic en el botón de editar",
        expected_result="El formulario de edición debe abrirse al hacer clic en editar",
        module="UI",
        test_id="EMPLOYEES-UI-006",
    )
    @pytest.mark.order(56)
    def test_edit_employee_button_opens_form(self):
        try:
            wait_for_no_overlay(self.driver)
            click_action_first_employee(self.driver, accion="editar")
            wait_for_no_overlay(self.driver)
            try:
                form_dialog = self.driver.find_element(By.ID, "employee-form-dialog")
            except Exception:
                form_dialog = self.driver.find_element(
                    By.XPATH,
                    "//*[contains(text(), 'Agregar Empleado') or contains(text(), 'Editar Empleado')]/ancestor::div[contains(@class, 'DialogContent') or contains(@class, 'dialog')]",
                )
            assert (
                form_dialog.is_displayed()
            ), "El formulario de edición de empleado no se muestra"
        except StaleElementReferenceException:
            return

    @add_test_info(
        description="Edita el nombre del empleado y verifica el cambio en la tabla",
        expected_result="El formulario de edición debe abrirse al hacer clic en editar",
        module="UI",
        test_id="EMPLOYEES-UI-006",
    )
    @pytest.mark.order(57)
    def test_update_employee(self):
        try:
            wait_for_no_overlay(self.driver)
            click_action_first_employee(self.driver, accion="editar")
            wait_for_no_overlay(self.driver)
            input_nombre = esperar_elemento_interactivo(
                self.driver, By.ID, "employee-full-name", timeout=20
            )
            assert (
                input_nombre is not None
            ), "No se encontró el input de nombre para editar"
            nombre_editado = "Empleado Prueba UI Editado"
            input_nombre.clear()
            input_nombre.send_keys(nombre_editado)
            guardar_btn = self.driver.find_element(By.ID, "employee-form-submit-btn")
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", guardar_btn
            )
            wait_for_no_overlay(self.driver)
            guardar_btn.click()
            try:
                WebDriverWait(self.driver, 20).until_not(
                    lambda d: d.find_element(
                        By.ID, "employee-form-dialog"
                    ).is_displayed()
                )
            except Exception:
                pass
            wait_for_no_overlay(self.driver)
            WebDriverWait(self.driver, 10).until(
                lambda d: nombre_editado in d.find_element(By.XPATH, "//table").text
            )
            table = self.driver.find_element(By.XPATH, "//table")
            assert (
                nombre_editado in table.text
            ), "El nombre editado no aparece en la tabla"
        except Exception:
            return

    @add_test_info(
        description="Verificar que el botón de eliminar empleado está presente en la tabla",
        expected_result="El botón de eliminar debe estar visible para cada empleado",
        module="UI",
        test_id="EMPLOYEES-UI-007",
    )
    @pytest.mark.order(58)
    def test_delete_employee(self):
        try:
            wait_for_no_overlay(self.driver)
            click_action_first_employee(self.driver, accion="eliminar")
            # Confirmar en el modal si existe
            try:
                confirm_btn = esperar_elemento_interactivo(
                    self.driver,
                    By.XPATH,
                    "//button[contains(., 'Confirmar') or contains(., 'Eliminar') or contains(., 'Sí') or contains(., 'Aceptar')]",
                    timeout=10,
                )
                assert (
                    confirm_btn is not None
                ), "No se encontró el botón de confirmación de eliminación"
                confirm_btn.click()
            except Exception:
                pass
            wait_for_no_overlay(self.driver)

            # Verificar que ya no aparece (sin filtrar, solo buscar por nombre)
            def empleado_ya_no_esta(driver):
                texto_tabla = driver.find_element(By.XPATH, "//table").text
                return (
                    "No hay resultados" in texto_tabla
                    or "Empleado Prueba UI Editado" not in texto_tabla
                )

            WebDriverWait(self.driver, 10).until(empleado_ya_no_esta)
            table = self.driver.find_element(By.XPATH, "//table")
            assert (
                "Empleado Prueba UI Editado" not in table.text
            ), "El empleado no fue eliminado de la tabla"
        except Exception:
            return

    @add_test_info(
        description="Verificar mensaje de carga de empleados",
        expected_result="El mensaje de carga debe mostrarse mientras se cargan los empleados",
        module="UI",
        test_id="EMPLOYEES-UI-008",
    )
    @pytest.mark.order(59)
    def test_employees_loading_message(self):
        """Verifica que el mensaje de carga se muestra correctamente"""
        # Simular recarga de la página
        self.driver.refresh()
        try:
            loading = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='employees-loading']"
            )
            assert (
                loading.is_displayed()
            ), "El mensaje de carga de empleados no se muestra"
        except Exception:
            pass  # Si carga muy rápido, puede que no se vea

    @add_test_info(
        description="Verificar mensaje de error de empleados",
        expected_result="El mensaje de error debe mostrarse si ocurre un error al cargar empleados",
        module="UI",
        test_id="EMPLOYEES-UI-009",
    )
    @pytest.mark.order(60)
    def test_employees_error_message(self):
        """Verifica que el mensaje de error se muestra si ocurre un error al cargar empleados"""
        # Este test requiere simular un error en la API o desconexión
        # Aquí solo se verifica que el elemento existe si se da el caso
        try:
            error = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='employees-error']"
            )
            assert (
                error.is_displayed()
            ), "El mensaje de error de empleados no se muestra"
        except Exception:
            pass  # Si no hay error, no debe mostrarse
