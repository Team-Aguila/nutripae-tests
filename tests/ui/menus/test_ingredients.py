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


class IngredientsLocators(Enum):
    """Enum de locators para elementos de la página de ingredientes"""

    # Login page
    LOGIN_EMAIL = (By.CSS_SELECTOR, "[name='email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "[name='password']")
    LOGIN_SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    # Navigation
    SIDEBAR_TOGGLE = (By.CSS_SELECTOR, "#sidebar-toggle-btn")
    NAV_MENUS_TRIGGER = (By.CSS_SELECTOR, "#nav-menus-section-trigger")
    NAV_INGREDIENTS = (By.CSS_SELECTOR, "#nav-ingredients")

    # Main page
    INGREDIENTS_PAGE = (By.CSS_SELECTOR, "#ingredients-page")
    INGREDIENTS_TITLE = (By.CSS_SELECTOR, "#ingredients-title")
    ADD_INGREDIENT_BTN = (By.CSS_SELECTOR, "#add-ingredient-btn")
    SEARCH_INPUT = (By.CSS_SELECTOR, "[data-testid='search-input']")
    DATA_TABLE = (By.CSS_SELECTOR, "[data-slot='table-container'] table")
    DATA_TABLE_ROWS = (By.CSS_SELECTOR, "[data-slot='table-container'] table tbody tr")
    DATA_TABLE_ACTION_OPEN_BTN = (
        By.CSS_SELECTOR,
        "[data-slot='table-container'] table tbody button",
    )
    ACTION_TOGGLE_BUTTON = (
        By.CSS_SELECTOR,
        "#toggle-status-ingredient",
    )
    ACTION_DELETE_BUTTON = (
        By.CSS_SELECTOR,
        "#delete-ingredient",
    )
    STATUS_LABEL_OF_ROW = (
        By.CSS_SELECTOR,
        "[data-slot='table-container'] table tbody tr .ingredient-status-label",
    )

    # Form dialog
    INGREDIENT_FORM_DIALOG = (By.CSS_SELECTOR, "#ingredient-form-dialog")
    INGREDIENT_FORM = (By.CSS_SELECTOR, "#ingredient-form")
    INGREDIENT_FORM_TITLE = (By.CSS_SELECTOR, "#ingredient-form-title")
    INGREDIENT_FORM_CANCEL_BTN = (By.CSS_SELECTOR, "#ingredient-form-cancel-btn")
    INGREDIENT_FORM_SUBMIT_BTN = (By.CSS_SELECTOR, "#ingredient-form-submit-btn")

    # Form fields
    INGREDIENT_NAME_INPUT = (By.CSS_SELECTOR, "#ingredient-name-input")
    INGREDIENT_NAME_ERROR = (By.CSS_SELECTOR, "#ingredient-name-error")
    INGREDIENT_UNIT_SELECT = (By.CSS_SELECTOR, "#ingredient-unit-select + select")
    INGREDIENT_CATEGORY_SELECT = (
        By.CSS_SELECTOR,
        "#ingredient-category-select + select",
    )
    INGREDIENT_DESCRIPTION_INPUT = (By.CSS_SELECTOR, "#ingredient-description-input")
    INGREDIENT_STATUS_SELECT = (By.CSS_SELECTOR, "#ingredient-status-select")

    # Actions
    EDIT_INGREDIENT_BTN = (By.CSS_SELECTOR, "[data-testid='edit-ingredient-btn']")
    INGREDIENT_TOGGLE_STATUS_BTN = (By.CSS_SELECTOR, "#toggle-status-ingredient")
    DELETE_CONFIRMATION_MODAL = (By.CSS_SELECTOR, "[role='alertdialog']")
    DELETE_CONFIRMATION_MODAL_BUTTON = (
        By.CSS_SELECTOR,
        "[role='alertdialog'] #confirm-button",
    )

    @property
    def by(self) -> str:
        """Retorna el tipo de By (CSS_SELECTOR, ID, etc.)"""
        return self.value[0]

    @property
    def selector(self) -> str:
        """Retorna el selector del elemento"""
        return self.value[1]

    def find_element(self, driver: webdriver.Chrome):
        """Encuentra un elemento usando este locator"""
        return driver.find_element(self.by, self.selector)

    def find_elements(self, driver: webdriver.Chrome):
        """Encuentra múltiples elementos usando este locator"""
        return driver.find_elements(self.by, self.selector)

    def wait_until_present(
        self, driver: webdriver.Chrome, timeout: int = DEFAULT_TIMEOUT
    ):
        """Espera hasta que el elemento esté presente"""
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((self.by, self.selector))
        )

    def wait_until_clickable(
        self, driver: webdriver.Chrome, timeout: int = DEFAULT_TIMEOUT
    ):
        """Espera hasta que el elemento sea clickeable"""
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((self.by, self.selector))
        )

    def wait_until_invisible(
        self, driver: webdriver.Chrome, timeout: int = DEFAULT_TIMEOUT
    ):
        """Espera hasta que el elemento se vuelva invisible"""
        return WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((self.by, self.selector))
        )

    def wait_until_visible(
        self, driver: webdriver.Chrome, timeout: int = DEFAULT_TIMEOUT
    ):
        """Espera hasta que el elemento sea visible"""
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((self.by, self.selector))
        )

    def is_present(self, driver: webdriver.Chrome) -> bool:
        """Verifica si el elemento está presente sin esperar"""
        try:
            driver.find_element(self.by, self.selector)
            return True
        except:
            return False

    def is_visible(self, driver: webdriver.Chrome) -> bool:
        """Verifica si el elemento es visible sin esperar"""
        try:
            element = driver.find_element(self.by, self.selector)
            return element.is_displayed()
        except:
            return False

    def wait_until_enabled(
        self, driver: webdriver.Chrome, timeout: int = DEFAULT_TIMEOUT
    ):
        """Espera hasta que el elemento esté habilitado"""
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((self.by, self.selector))
        )


class TestIngredientsUI:
    """Suite de pruebas de UI para Ingredientes"""

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
        username_input = IngredientsLocators.LOGIN_EMAIL.wait_until_present(cls.driver)
        password_input = IngredientsLocators.LOGIN_PASSWORD.find_element(cls.driver)
        login_button = IngredientsLocators.LOGIN_SUBMIT.find_element(cls.driver)

        username_input.clear()
        username_input.send_keys(settings.ADMIN_USER_EMAIL)
        password_input.clear()
        password_input.send_keys(settings.ADMIN_USER_PASSWORD)
        login_button.click()

        # Esperar a que cargue el dashboard
        IngredientsLocators.SIDEBAR_TOGGLE.wait_until_present(cls.driver)

    @classmethod
    def _go_to_ingredients_page(cls):
        """Navegar a la página de ingredientes"""
        menus_dropdown = IngredientsLocators.NAV_MENUS_TRIGGER.find_element(cls.driver)
        menus_dropdown.click()

        IngredientsLocators.NAV_INGREDIENTS.wait_until_present(cls.driver)
        ingredients_link = IngredientsLocators.NAV_INGREDIENTS.find_element(cls.driver)
        ingredients_link.click()

        # Esperar a que cargue la página de ingredientes
        IngredientsLocators.ADD_INGREDIENT_BTN.wait_until_present(cls.driver)

    @add_test_info(
        description="Verificar que la página de ingredientes carga correctamente",
        expected_result="La página de ingredientes debe cargar sin errores",
        module="UI",
        test_id="INGREDIENTS-UI-001",
    )
    @pytest.mark.order(1)
    def test_ingredients_page_loads(self):
        """Verificar que la página de ingredientes carga correctamente"""
        # Verificar que los elementos principales están presentes
        page_container = IngredientsLocators.INGREDIENTS_PAGE.wait_until_present(
            self.driver
        )
        assert page_container.is_displayed(), "El contenedor de la página no se muestra"

        # Verificar título de la página
        title = IngredientsLocators.INGREDIENTS_TITLE.wait_until_present(self.driver)
        assert "Ingredientes" in title.text, "El título de la página no es correcto"

        # Verificar botón de agregar
        add_button = IngredientsLocators.ADD_INGREDIENT_BTN.find_element(self.driver)
        assert add_button.is_displayed(), "El botón de agregar no se muestra"

    @add_test_info(
        description="Verificar la creacion del botón de agregar ingrediente",
        expected_result="El botón de agregar ingrediente debe estar visible",
        module="UI",
        test_id="INGREDIENTS-UI-002",
    )
    @pytest.mark.order(2)
    def test_add_ingredient_button(self):
        """Verificar que el botón de agregar ingrediente está visible"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/ingredients")

        # Verificar que el botón de agregar ingrediente está presente
        add_button = IngredientsLocators.ADD_INGREDIENT_BTN.wait_until_present(
            self.driver
        )
        assert add_button.is_displayed(), "El botón de agregar no se muestra"
        assert (
            "Agregar Ingrediente" in add_button.text
        ), "El texto del botón no es correcto"
        add_button.click()

        # Esperar a que se abra el modal de creación de ingrediente
        form_title = IngredientsLocators.INGREDIENT_FORM_TITLE.wait_until_present(
            self.driver
        )
        assert form_title.is_displayed(), "El título del formulario no se muestra"

        # Verificar que el modal se ha abierto
        cancel_button = IngredientsLocators.INGREDIENT_FORM_CANCEL_BTN.find_element(
            self.driver
        )
        save_button = IngredientsLocators.INGREDIENT_FORM_SUBMIT_BTN.find_element(
            self.driver
        )
        assert cancel_button.is_displayed(), "El botón de cancelar no se muestra"
        assert save_button.is_displayed(), "El botón de guardar no se muestra"

        # Probar campo de nombre
        ingredient_name_input = IngredientsLocators.INGREDIENT_NAME_INPUT.find_element(
            self.driver
        )
        assert ingredient_name_input.is_displayed(), "El campo de nombre no se muestra"
        ingredient_name_input.clear()
        ingredient_name_input.send_keys(f"Test Ingrediente {self.TIMESTAMP}")
        assert (
            ingredient_name_input.get_attribute("value") == f"Test Ingrediente {self.TIMESTAMP}"  # type: ignore
        ), "El campo de nombre no se ha actualizado correctamente"

        # Probar selector de unidad
        ingredient_unit_selector = Select(
            (IngredientsLocators.INGREDIENT_UNIT_SELECT.find_element(self.driver))
        )
        ingredient_unit_selector.select_by_value("cucharadas")
        assert (
            ingredient_unit_selector.first_selected_option.text.lower()
            == "Cucharadas".lower()
        ), "La unidad seleccionada no es correcta"

        # Probar selector de categoría
        category_selector = Select(
            IngredientsLocators.INGREDIENT_CATEGORY_SELECT.find_element(self.driver)
        )
        category_selector.select_by_value("sin_categoria")
        assert (
            category_selector.first_selected_option.text == "Sin categoría"
        ), "La categoría seleccionada no es correcta"

        # Guardar formulario
        IngredientsLocators.INGREDIENT_FORM_SUBMIT_BTN.wait_until_clickable(self.driver)
        save_button.click()

        # Esperar a que se cierre el modal
        IngredientsLocators.INGREDIENT_FORM.wait_until_invisible(self.driver)

    @add_test_info(
        description="Verificar que el ingrediente es visible en la tabla después de agregarlo",
        expected_result="El ingrediente debe aparecer en la tabla de ingredientes",
        module="UI",
        test_id="INGREDIENTS-UI-003",
    )
    @pytest.mark.order(3)
    def test_ingredient_appears_in_table(self):
        """Verificar que el ingrediente agregado aparece en la tabla"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/ingredients")

        # Verificar que la tabla de ingredientes está visible
        data_table = IngredientsLocators.DATA_TABLE.wait_until_present(self.driver)
        assert data_table.is_displayed(), "La tabla de ingredientes no se muestra"

        # Verificar que el nuevo ingrediente aparece en la tabla
        rows = IngredientsLocators.DATA_TABLE_ROWS.find_elements(self.driver)
        assert len(rows) > 0, "No hay filas en la tabla de ingredientes"

        # Comprobar que el último ingrediente agregado está presente
        last_row = rows[-1]
        assert (
            f"Test Ingrediente {self.TIMESTAMP}" in last_row.text
        ), "El ingrediente recién agregado no aparece en la tabla"

    @add_test_info(
        description="Verificar funcionalidad de validación del formulario",
        expected_result="El formulario debe mostrar errores cuando los campos requeridos están vacíos",
        module="UI",
        test_id="INGREDIENTS-UI-004",
    )
    @pytest.mark.order(4)
    def test_ingredient_form_validation(self):
        """Verificar validación del formulario de ingredientes"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/ingredients")

        # Abrir formulario
        add_button = IngredientsLocators.ADD_INGREDIENT_BTN.wait_until_clickable(
            self.driver
        )
        add_button.click()

        # Intentar enviar formulario vacío
        submit_button = (
            IngredientsLocators.INGREDIENT_FORM_SUBMIT_BTN.wait_until_clickable(
                self.driver
            )
        )
        submit_button.click()

        # Verificar que aparecen errores de validación
        name_error = IngredientsLocators.INGREDIENT_NAME_ERROR.wait_until_present(
            self.driver
        )
        assert (
            name_error.is_displayed()
        ), "No se muestra error de validación para nombre"
        assert (
            "requerido" in name_error.text.lower()
        ), "El mensaje de error no es correcto"

    @add_test_info(
        description="Verificar que los botones de activar/desactivar funcionan correctamente",
        expected_result="Los botones de activar/desactivar deben cambiar el estado del ingrediente",
        module="UI",
        test_id="INGREDIENTS-UI-005",
    )
    @pytest.mark.order(5)
    def test_toggle_ingredient_active_state(self):
        """Verificar que los botones de activar/desactivar funcionan correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/ingredients")

        # Verificar que la tabla de ingredientes está visible
        data_table = IngredientsLocators.DATA_TABLE.wait_until_present(self.driver)
        assert data_table.is_displayed(), "La tabla de ingredientes no se muestra"

        # Verificar que hay filas en la tabla
        rows = IngredientsLocators.DATA_TABLE_ROWS.find_elements(self.driver)
        assert len(rows) > 0, "No hay filas en la tabla de ingredientes"

        #  Abrir opcion de activar/desactivar
        IngredientsLocators.DATA_TABLE_ACTION_OPEN_BTN.wait_until_present(self.driver)
        action_open_btn_list = (
            IngredientsLocators.DATA_TABLE_ACTION_OPEN_BTN.find_elements(self.driver)
        )
        action_open_btn = action_open_btn_list[-1]
        action_open_btn.click()

        IngredientsLocators.INGREDIENT_TOGGLE_STATUS_BTN.wait_until_visible(self.driver)

        # Verificar que el botón de activar/desactivar está presente
        toggle_button = IngredientsLocators.INGREDIENT_TOGGLE_STATUS_BTN.find_element(
            self.driver
        )
        assert (
            toggle_button.is_displayed()
        ), "El botón de activar/desactivar no se muestra"

        # Verificar el estado actual del ingrediente
        rows_labels = IngredientsLocators.STATUS_LABEL_OF_ROW.find_elements(self.driver)
        assert len(rows_labels) > 0, "No hay etiquetas de estado en la tabla"

        # Tomar el primer estado y verificar su texto
        toggle_button.click()
        self.driver.refresh()
        IngredientsLocators.DATA_TABLE.wait_until_present(self.driver)
        rows_labels = IngredientsLocators.STATUS_LABEL_OF_ROW.find_elements(self.driver)
        assert len(rows_labels) > 0, "No hay etiquetas de estado en la tabla"

    @add_test_info(
        description="Verificar que el botón de eliminar ingrediente funciona correctamente",
        expected_result="El ingrediente debe eliminarse de la lista después de confirmar",
        module="UI",
        test_id="INGREDIENTS-UI-006",
    )
    @pytest.mark.order(6)
    def test_delete_ingredient(self):
        """Verificar que el botón de eliminar ingrediente funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/ingredients")

        # Verificar que la tabla de ingredientes está visible
        data_table = IngredientsLocators.DATA_TABLE.wait_until_present(self.driver)
        assert data_table.is_displayed(), "La tabla de ingredientes no se muestra"

        # Verificar que hay filas en la tabla
        rows = IngredientsLocators.DATA_TABLE_ROWS.find_elements(self.driver)
        assert len(rows) > 0, "No hay filas en la tabla de ingredientes"

        #  Abrir opcion de eliminar
        IngredientsLocators.DATA_TABLE_ACTION_OPEN_BTN.wait_until_present(self.driver)
        action_open_btn = IngredientsLocators.DATA_TABLE_ACTION_OPEN_BTN.find_element(
            self.driver
        )
        action_open_btn.click()

        rows_btn = IngredientsLocators.ACTION_DELETE_BUTTON.find_elements(self.driver)
        assert len(rows_btn) > 0, "No hay filas en la tabla de ingredientes"
        total_rows = len(rows_btn)

        # Tomar el primer ingrediente y hacer clic en eliminar
        first_row_btn = rows_btn[0]
        first_row_btn.click()

        # Esperar a que aparezca el modal de confirmación
        confirmation_modal = (
            IngredientsLocators.DELETE_CONFIRMATION_MODAL.wait_until_visible(
                self.driver
            )
        )
        assert (
            confirmation_modal.is_displayed()
        ), "El modal de confirmación no se muestra"

        # Confirmar eliminación
        confirm_button = (
            IngredientsLocators.DELETE_CONFIRMATION_MODAL_BUTTON.find_element(
                self.driver
            )
        )
        confirm_button.click()

        # Esperar a que se cierre el modal y verificar que el ingrediente ya no está en la tabla
        IngredientsLocators.DELETE_CONFIRMATION_MODAL.wait_until_invisible(self.driver)
        self.driver.refresh()
        IngredientsLocators.DATA_TABLE.wait_until_present(self.driver)

        # Verificar que el ingrediente eliminado ya no está en la tabla
        rows = IngredientsLocators.DATA_TABLE_ROWS.find_elements(self.driver)
        assert (
            len(rows) >= 0
        ), "No hay filas en la tabla de ingredientes después de eliminar"
        assert (
            len(rows) == total_rows - 1
        ), "El número de filas en la tabla no ha disminuido correctamente después de eliminar"
