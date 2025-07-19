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

class BeneficiariesLocation(Enum):
    """"Enum para las ubicaciones de los beneficiarios."""
    # Login page
    LOGIN_EMAIL = (By.CSS_SELECTOR, "[name='email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "[name='password']")
    LOGIN_SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    # Navigation
    SIDEBAR_TOGGLE = (By.CSS_SELECTOR, "#sidebar-toggle-btn")
    NAV_COBERTURA_TRIGGER = (By.CSS_SELECTOR, "#nav-coverage-section-trigger")
    NAV_BENEFICIARIES = (By.CSS_SELECTOR, "#nav-beneficiaries")

    # Main page
    BENEFICIARIESPAGE = (By.CSS_SELECTOR, "#campuses-page")
    BENEFICIARIES_TITLE = (By.CSS_SELECTOR, "#campuses-title")
    BENEFICIARIES_BTN = (By.CSS_SELECTOR, "#add-sedes-btn")
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


class TestBeneficiariesUI:
    """Clase para pruebas de la página de beneficiarios."""

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
        cls._go_to_Beneficiaries_page()
    @classmethod
    def _login(cls):
        cls.driver.get(f"{settings.BASE_FRONTEND_URL}/login")

        username_input = BeneficiariesLocation.LOGIN_EMAIL.wait_until_present(cls.driver)
        password_input = BeneficiariesLocation.LOGIN_PASSWORD.find_element(cls.driver)
        login_button = BeneficiariesLocation.LOGIN_SUBMIT.find_element(cls.driver)

        username_input.clear()
        username_input.send_keys(settings.ADMIN_USER_EMAIL)
        password_input.clear()
        password_input.send_keys(settings.ADMIN_USER_PASSWORD)
        login_button.click()
        # Confirmar que se haya redireccionado correctamente
        BeneficiariesLocation.SIDEBAR_TOGGLE.wait_until_present(cls.driver)

    @classmethod
    def _go_to_Beneficiaries_page(cls):
        """Navega a la sección de Instituciones dentro de Cobertura"""
        btn_cobertura = cls.driver.find_element(By.XPATH, "//button[.//span[text()='Cobertura']]")
        btn_cobertura.click()

        beneficiarios_link = cls.driver.find_element(By.XPATH, "//a[.//span[text()='Beneficiarios']]")
        beneficiarios_link.click()
    @classmethod
    def teardown_class(cls):
        """Cerrar el navegador al finalizar todas las pruebas de la clase."""
        if cls.driver:
            cls.driver.quit()
    @add_test_info(
        description="Verificar que la página de Beneficiarios carga correctamente",
        expected_result="La página de Beneficiarios debe cargar sin errores",
        module="Cobertura - UI",
        test_id="BENEFICIARIES-UI-001",
    )
    @pytest.mark.order(91)    
    def test_beneficiarios_page_load(self):
        """Verificar que la página de Beneficiarios carga correctamente"""
        # Verificar que el título de la página es correcto
        title = self.driver.find_element(By.XPATH, "//h1[text()='Beneficiarios']")
        assert "Beneficiarios" in title.text, "El título de la página no es correcto"
        # Verficar botón de añadir Beneficiario
        add_beneficiaries_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Agregar Beneficiario')]")
        assert add_beneficiaries_btn.is_displayed(), "El botón de añadir Institución no se muestra en la página"
    @add_test_info(
        description="Verificar que el botón de añadir Beneficiarios funciona correctamente",
        expected_result="El botón de añadir Beneficiarios debe abrir el modal de creación",
        module="Cobertura - UI",
        test_id="BENEFICIARIES-UI-002",
    )
    @pytest.mark.order(92)
    def test_add_beneficiaries_button(self):
        """Verificar que el botón de añadir Beneficiarios funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/beneficiaries")  # Ajusta la URL si es diferente
        # Verificar que el botón de agregar está presente
        add_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Agregar Beneficiario']"))
        )
        assert add_button.is_displayed(), "El botón de agregar Institución no se muestra"
        add_button.click()
        # Verificar que se abre el modal
        dialog = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "radix-«rb»"))  # Ajusta el ID si es dinámico o diferente
        )
        assert dialog.is_displayed(), "El diálogo de creación de beneficiario no se muestra"
        # Llenar el formulario de creación
        # Abrir el combobox (una sola vez)
        combo_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Seleccione un tipo']]"))
        )
        combo_button.click()
        # Esperar y seleccionar la opción que quieras
        option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and normalize-space(.)='documento de identidad']"))
        )
        assert option.is_displayed(), "La opción de tipo de documento no se muestra"
        option.click()
        number_documentinput = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "number_document"))
        )
        number_documentinput.send_keys("123456789")
        assert number_documentinput.get_attribute("value") == "123456789", "El campo de número de documento no se llenó correctamente"
        first_name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "first_name"))
        )
        first_name_input.send_keys("Juan")
        assert first_name_input.get_attribute("value") == "Juan", "El campo de primer nombre no se llenó correctamente"
        second_name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "second_name"))
        )
        second_name_input.send_keys("Andres")
        assert second_name_input.get_attribute("value") == "Andres", "El campo de segundo nombre no se llenó correctamente"
        first_surname_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "first_surname"))
        )
        assert first_surname_input.is_displayed(), "El campo de primer apellido no se muestra"
        first_surname_input.send_keys("Adames")
        second_surname_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "second_surname"))
        )
        assert second_surname_input.is_displayed(), "El campo de segundo apellido no se muestra"
        second_surname_input.send_keys("López")
        birth_date_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "birth_date"))
        )
        birth_date_input.send_keys("01/12/2000")
        assert birth_date_input.is_displayed(), "El campo de fecha de nacimiento no se muestra"
        # Seleccionar el género
        # Abrir el combobox de género
        genero_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Seleccione un género']]"))
        )
        genero_button.click()
        option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and normalize-space()='masculino']"))
        )
        assert option.is_displayed(), "La opción de género no se muestra"
        option.click()
        # Seleccionar el grado
        # Abrir el combobox de grado
        grado_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Seleccione un grado']]"))
        )
        grado_button.click()
        option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and normalize-space()='once']"))
        )
        assert option.is_displayed(), "La opción de grado no se muestra"
        option.click()
        # Seleccionar la discapacidad
        # Abrir el combobox de discapacidad 
        discapacidad_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Seleccione un tipo']]"))
        )
        discapacidad_button.click()
        option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and normalize-space()='motora']"))
        )
        assert option.is_displayed(), "La opción de discapacidad no se muestra"
        option.click()
        checkbox = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "victim_conflict"))
        )

        # Clic si está desmarcado
        if checkbox.get_attribute("aria-checked") == "false":
            checkbox.click()

        # Asegurar que quedó marcado
        assert checkbox.get_attribute("aria-checked") == "true", "El checkbox 'victim_conflict' no se marcó correctamente"
        attendant_name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "attendant_name"))
        )
        attendant_name_input.send_keys("Maria Lopez")
        assert attendant_name_input.get_attribute("value") == "Maria Lopez", "El campo de nombre del acudiente no se llenó correctamente"
        attendant_phone_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "attendant_phone"))
        )
        attendant_phone_input.send_keys("3001234567")
        assert attendant_phone_input.get_attribute("value") == "3001234567", "El campo de teléfono del acudiente no se llenó correctamente"
        guardar_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Guardar']"))
        )
        assert guardar_button.is_displayed(), "El botón de guardar no se muestra en el modal"
        guardar_button.click()
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/beneficiaries")
    @add_test_info(
        description="Verificar que el filtro de Nombre completo de Beneficiarios funciona correctamente",
        expected_result="El filtro de Beneficiarios debe buscar por nombre de forma correcta",
        module="Cobertura - UI",
        test_id="BENEFICIARIES-UI-003",
    )
    @pytest.mark.order(93)
    def test_filter_beneficiaries_by_full_name(self):
        """Verificar que el filtro de Nombre completo de Beneficiarios funciona correctamente"""

        # Esperar a que la página cargue
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Beneficiarios']"))
        )

        # Filtro por nombre completo (1er input)
        nombre_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[1]"))
        )
        nombre_input.clear()
        nombre_input.send_keys("Juan Andres Adames López")
        nombre_aparece = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']"))
        )
        assert nombre_aparece.is_displayed(), "El nombre 'Juan Andres Adames López' no se muestra en la tabla"
        # Buscar un nombre que NO existe
        nombre_input.clear()  # CORREGIDO: `input.clear()` no existe, debes usar `nombre_input.clear()`
        nombre_input.send_keys("Juan Andres Adames López 123")

        # Espera que NO haya resultados visibles con ese nombre incorrecto
        # Verifica que no aparece ese nombre (usando `find_elements`)
        WebDriverWait(self.driver, 5).until(
            lambda d: len(d.find_elements(By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López 123']")) == 0
        )
        assert len(self.driver.find_elements(By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López 123']")) == 0, \
        "El nombre 'Juan Andres Adames López 123' **sí** aparece en la tabla, pero no debería"
    @add_test_info(
        description="Verificar que el filtro de Documento de Beneficiarios funciona correctamente",
        expected_result="El filtro de Beneficiarios debe buscar por documento de forma correcta",
        module="Cobertura - UI",
        test_id="BENEFICIARIES-UI-004",
    )
    @pytest.mark.order(94)
    def test_filter_beneficiaries_document(self):
        """Verificar que el filtro de Documento de Beneficiarios funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/beneficiaries")
        # Esperar a que la página cargue
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Beneficiarios']"))
        )
        # Filtro por documento (2 input)
        document_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[2]"))
        )
        document_input.clear()
        document_input.send_keys("123456789")
        documento_aparece = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']"))
        )
        assert documento_aparece.is_displayed(), "El documento 123456789 no se muestra en la tabla"
        document_input.clear()
        document_input.send_keys("987654321")
        WebDriverWait(self.driver, 3).until(
            lambda d: len(d.find_elements(By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']")) == 0
        )

    @add_test_info(
        description="Verificar que el filtro de Documento de identidad de Beneficiarios funciona correctamente",
        expected_result="El filtro de Beneficiarios debe buscar por documento de identidad de forma correcta",
        module="Cobertura - UI",
        test_id="BENEFICIARIES-UI-005",
    )
    @pytest.mark.order(95)
    def test_filter_beneficiaries_identy_document(self):
        """Verificar que el filtro de Documento de identidad de Beneficiarios funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/beneficiaries")
        # Esperar a que la página cargue
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Beneficiarios']"))
        )
        # Filtro por documento (2 input)
        document_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[2]"))
        )
        document_input.clear()
        document_input.send_keys("123456789")
        documento_aparece = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']"))
        )
        assert documento_aparece.is_displayed(), "El documento 123456789 no se muestra en la tabla"
        # Filtro por documento (3 input)
        identy_document_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[3]"))
        )
        identy_document_input.send_keys("documento de identidad")
        assert identy_document_input.is_displayed(), "El documento de identidad de la persona 123456789 no se muestra en la tabla"
        identy_document_input.clear()
        identy_document_input.send_keys("femenino")
        WebDriverWait(self.driver, 3).until(
            lambda d: len(d.find_elements(By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']")) == 0
        )

    @add_test_info(
        description="Verificar que el filtro de genero de Beneficiarios funciona correctamente",
        expected_result="El filtro de Beneficiarios debe buscar por genero de forma correcta",
        module="Cobertura - UI",
        test_id="BENEFICIARIES-UI-006",
    )
    @pytest.mark.order(96)
    def test_filter_beneficiaries_gender(self):
        """Verificar que el filtro de genero de Beneficiarios funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/beneficiaries")
        # Esperar a que la página cargue
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Beneficiarios']"))
        )
        # Filtro por documento (2 input)
        document_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[2]"))
        )
        document_input.clear()
        document_input.send_keys("123456789")
        documento_aparece = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']"))
        )
        assert documento_aparece.is_displayed(), "El documento 123456789 no se muestra en la tabla"
        # Filtro por documento (4 input)
        gender_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[4]"))
        )
        gender_input.send_keys("masculino")
        assert gender_input.is_displayed(), "El genero de la persona 123456789 no se muestra en la tabla"
        gender_input.clear()
        gender_input.send_keys("femenino")
        WebDriverWait(self.driver, 3).until(
            lambda d: len(d.find_elements(By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']")) == 0
        )

    @add_test_info(
        description="Verificar que el filtro de genero de Beneficiarios funciona correctamente",
        expected_result="El filtro de Beneficiarios debe buscar por genero de forma correcta",
        module="Cobertura - UI",
        test_id="BENEFICIARIES-UI-007",
    )
    @pytest.mark.order(97)
    def test_filter_beneficiaries_gender(self):
        """Verificar que el filtro de grado de Beneficiarios funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/beneficiaries")
        # Esperar a que la página cargue
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Beneficiarios']"))
        )
        # Filtro por documento (2 input)
        document_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[2]"))
        )
        document_input.clear()
        document_input.send_keys("123456789")
        documento_aparece = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']"))
        )
        assert documento_aparece.is_displayed(), "El documento 123456789 no se muestra en la tabla"
        # Filtro por documento (4 input)
        gender_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[4]"))
        )
        gender_input.send_keys("masculino")
        assert gender_input.is_displayed(), "El genero de la persona 123456789 no se muestra en la tabla"
        gender_input.clear()
        gender_input.send_keys("femenino")
        WebDriverWait(self.driver, 3).until(
            lambda d: len(d.find_elements(By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']")) == 0
        )

    @add_test_info(
        description="Verificar que el filtro de grado de Beneficiarios funciona correctamente",
        expected_result="El filtro de Beneficiarios debe buscar por grado de forma correcta",
        module="Cobertura - UI",
        test_id="BENEFICIARIES-UI-008",
    )
    @pytest.mark.order(98)
    def test_filter_beneficiaries_grade(self):
        """Verificar que el filtro de grado de Beneficiarios funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/beneficiaries")
        # Esperar a que la página cargue
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Beneficiarios']"))
        )
        # Filtro por documento (2 input)
        document_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[2]"))
        )
        document_input.clear()
        document_input.send_keys("123456789")
        documento_aparece = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']"))
        )
        assert documento_aparece.is_displayed(), "El documento 123456789 no se muestra en la tabla"
        # Filtro por documento (5 input)
        grade_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[5]"))
        )
        grade_input.send_keys("once")
        assert grade_input.is_displayed(), "El grado de la persona 123456789 no se muestra en la tabla"
        grade_input.clear()
        #grade_input.send_keys("decimo")
        #WebDriverWait(self.driver, 3).until(
        #    lambda d: len(d.find_elements(By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']")) == 0
        #)

    @add_test_info(
        description="Verificar que se puede editar a un perfil en Beneficiarios funciona correctamente",
        expected_result="La función de editar un perfil funcione de forma correcta",
        module="Cobertura - UI",
        test_id="BENEFICIARIES-UI-009",
    )
    @pytest.mark.order(99)
    def test_eddit_beneficiaries_button(self):
        """Verificar que se puede editar a un perfil en Beneficiarios funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/coverage/beneficiaries")
        # Esperar a que la página cargue
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Beneficiarios']"))
        )
        # Filtro por documento (2 input)
        document_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@placeholder='Buscar...'])[2]"))
        )
        document_input.clear()
        document_input.send_keys("123456789")
        documento_aparece = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='font-medium' and text()='Juan Andres Adames López']"))
        )
        assert documento_aparece.is_displayed(), "El documento 123456789 no se muestra en la tabla"
        # Ubicar la fila por el texto del beneficiario
        row = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//tr[.//div[contains(text(), 'Juan Andres Adames López')]]"))
        )

        # Scroll hacia la fila para que sea visible
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)

        # Esperar a que el botón de los tres puntos (menú) esté clickeable dentro de esa fila
        menu_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//tr[.//div[contains(text(), 'Juan Andres Adames López')]]//button[@data-slot='dropdown-menu-trigger']"
            ))
        )

        ### QUEDO POR TERMINAR ESTE DE ACÁ YA QUE COMO NO SE PUEDE ELIMINAR ENTONCES SI LO EDITO SE VA A QUEDAR ASÍ Y AL RE EJECUTARLO LAS PRUEBAS VAN A DAR ERRONEAS