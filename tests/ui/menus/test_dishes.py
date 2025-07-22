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

from tests.ui.menus.test_ingredients import IngredientsLocators

DEFAULT_TIMEOUT = 20  # Tiempo por defecto para esperas


class DishesLocators(Enum):
    """Locators para la página de platos"""

    # Formulario de creación de platos
    ADD_DISH_BTN = (By.CSS_SELECTOR, "#add-dish-button")
    DISH_FORM_TITLE = (By.CSS_SELECTOR, "#dish-form-title")
    DISH_FORM_CANCEL_BTN = (By.CSS_SELECTOR, "#dish-form-cancel-button")
    DISH_FORM_SUBMIT_BTN = (By.CSS_SELECTOR, "#dish-form-submit-button")
    ## Información del plato
    DISH_NAME_INPUT = (By.CSS_SELECTOR, "#dish-name-input")
    DISH_DESCRIPTION_INPUT = (By.CSS_SELECTOR, "#dish-description-input")
    DISH_STATUS_SELECT = (By.CSS_SELECTOR, "#dish-status-select + select")
    DISH_MEAL_TYPE_DESAYUNO = (By.CSS_SELECTOR, "#dish-meal-type-desayuno")
    ## Seleccion de ingredientes
    DISH_INGREDIENTS_SELECT = (By.CSS_SELECTOR, "#ingredient-select-0 + select")
    DISH_INGREDIENT_QUANTITY_INPUT = (By.CSS_SELECTOR, "#ingredient-quantity-0")
    ## Información nutricional
    DISH_NUTRITIONAL_INFO_CALORIES = (By.CSS_SELECTOR, "#dish-calories-input")
    DISH_NUTRITIONAL_INFO_PROTEIN = (By.CSS_SELECTOR, "#dish-protein-input")

    # Tabla de platos
    DATA_TABLE = (By.CSS_SELECTOR, "#dishes-table")
    DATA_TABLE_ROWS = (By.CSS_SELECTOR, "#dishes-table tbody tr")
    ### Context: Los botones de acción tienen IDs dinámicos con el inicio "dish-actions-", para esto usamos un XPath
    ### pero no es recomendable usar XPath en otros escenarios a menos que sea necesario
    DATA_TABLE_ACTION_OPEN_BTN = (By.XPATH, "//button[contains(@id, 'dish-actions-')]")
    ACTION_DISABLE_BUTTON = (By.XPATH, "//div[contains(@id, 'dish-toggle-status-')]")

    # Modal de confirmación de eliminación
    DISABLE_CONFIRMATION_MODAL = (By.CSS_SELECTOR, "[role='alertdialog']")
    DISABLE_CONFIRMATION_MODAL_BUTTON = (
        By.CSS_SELECTOR,
        "#confirm-button",
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


class TestDishesUI:
    """Suite de pruebas de UI para platos"""

    driver: webdriver.Chrome
    TIMESTAMP = datetime.now(tz.utc).strftime("%Y-%m-%d %H:%M:%S")

    TEMPORAL_INGREDIENT_STATUS = None

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
        cls._create_ingredient()

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
    def _create_ingredient(cls):
        cls.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/ingredients")

        # Verificar que el ingrediente temporal no existe
        rows = IngredientsLocators.DATA_TABLE_ROWS.find_elements(cls.driver)
        for row in rows:
            if f"Test Ingrediente Temporal" in row.text:
                cls.TEMPORAL_INGREDIENT_STATUS = True  # type: ignore
                return  # Si ya existe, no crear de nuevo

        # Verificar que el botón de agregar ingrediente está presente
        add_button = IngredientsLocators.ADD_INGREDIENT_BTN.wait_until_present(
            cls.driver
        )
        add_button.click()

        # Esperar a que se abra el modal de creación de ingrediente
        IngredientsLocators.INGREDIENT_FORM_TITLE.wait_until_present(cls.driver)

        # Verificar que el modal se ha abierto
        IngredientsLocators.INGREDIENT_FORM_CANCEL_BTN.find_element(cls.driver)
        save_button = IngredientsLocators.INGREDIENT_FORM_SUBMIT_BTN.find_element(
            cls.driver
        )

        # Probar campo de nombre
        ingredient_name_input = IngredientsLocators.INGREDIENT_NAME_INPUT.find_element(
            cls.driver
        )
        ingredient_name_input.clear()
        ingredient_name_input.send_keys(f"Test Ingrediente Temporal")

        # Probar selector de unidad
        ingredient_unit_selector = Select(
            (IngredientsLocators.INGREDIENT_UNIT_SELECT.find_element(cls.driver))
        )
        ingredient_unit_selector.select_by_value("cucharadas")

        # Probar selector de categoría
        category_selector = Select(
            IngredientsLocators.INGREDIENT_CATEGORY_SELECT.find_element(cls.driver)
        )
        category_selector.select_by_value("sin_categoria")

        # Guardar formulario
        IngredientsLocators.INGREDIENT_FORM_SUBMIT_BTN.wait_until_clickable(cls.driver)
        save_button.click()

        # Esperar a que se cierre el modal
        IngredientsLocators.INGREDIENT_FORM.wait_until_invisible(cls.driver)

        cls.TEMPORAL_INGREDIENT_STATUS = True  # type: ignore

    @add_test_info(
        description="Verifica que la página de platos carga correctamente",
        expected_result="La página de platos se carga sin errores",
        module="UI",
        test_id="DISHES-UI-001",
    )
    @pytest.mark.order(7)
    def test_dish_page_loads(self):
        """Verificar que la página de platos carga correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/dishes")

        # Verificar que el botón de agregar plato está presente
        DishesLocators.ADD_DISH_BTN.wait_until_present(self.driver)
        assert DishesLocators.ADD_DISH_BTN.is_visible(
            self.driver
        ), "Botón de agregar plato no visible"

    @add_test_info(
        description="Verificar la creación del botón de agregar plato",
        expected_result="El botón de agregar plato debe estar visible y funcional",
        module="UI",
        test_id="DISHES-UI-002",
    )
    @pytest.mark.order(8)
    def test_add_dish_button(self):
        """Verificar que el botón de agregar plato está visible y funciona correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/dishes")

        # Verificar que el botón de agregar plato está presente
        DishesLocators.ADD_DISH_BTN.wait_until_present(self.driver)

        add_button = DishesLocators.ADD_DISH_BTN.find_element(self.driver)
        assert add_button.is_displayed(), "Botón de agregar plato no visible"

        # Hacer clic en el botón de agregar plato
        add_button.click()

        # Verificar que se abre el formulario de creación de plato
        DishesLocators.DISH_FORM_TITLE.wait_until_present(self.driver)
        assert DishesLocators.DISH_FORM_TITLE.is_visible(
            self.driver
        ), "Formulario de creación de plato no visible"

        cancel_button = DishesLocators.DISH_FORM_CANCEL_BTN.find_element(self.driver)
        assert cancel_button.is_displayed(), "Botón de cancelar formulario no visible"
        submit_button = DishesLocators.DISH_FORM_SUBMIT_BTN.find_element(self.driver)
        assert submit_button.is_displayed(), "Botón de enviar formulario no visible"

        # Probar campos de nombre y descripción
        dish_name_input = DishesLocators.DISH_NAME_INPUT.find_element(self.driver)
        dish_description_input = DishesLocators.DISH_DESCRIPTION_INPUT.find_element(
            self.driver
        )
        dish_name_input.clear()
        dish_name_input.send_keys(f"Test Plato {self.TIMESTAMP}")
        dish_description_input.clear()
        dish_description_input.send_keys("Descripción del plato de prueba")

        # Probar selector de meal type
        meal_type_selector = DishesLocators.DISH_MEAL_TYPE_DESAYUNO.find_element(
            self.driver
        )
        meal_type_selector.click()
        assert (
            meal_type_selector.get_attribute("aria-checked") == "true"  # type: ignore
        ), "Tipo de comida no seleccionado correctamente"

        # Probar receta de ingredientes
        ingredient_select = Select(
            DishesLocators.DISH_INGREDIENTS_SELECT.find_element(self.driver)
        )
        ingredient_select.select_by_visible_text("Test Ingrediente Temporal")
        assert (
            ingredient_select.first_selected_option.text.lower()
            == "Test Ingrediente Temporal".lower()
        ), "Ingrediente no seleccionado correctamente"

        quantity_input = DishesLocators.DISH_INGREDIENT_QUANTITY_INPUT.find_element(
            self.driver
        )
        quantity_input.clear()
        quantity_input.send_keys("100")

        # Probar información nutricional
        calories_input = DishesLocators.DISH_NUTRITIONAL_INFO_CALORIES.find_element(
            self.driver
        )
        protein_input = DishesLocators.DISH_NUTRITIONAL_INFO_PROTEIN.find_element(
            self.driver
        )
        calories_input.clear()
        calories_input.send_keys("250")
        protein_input.clear()
        protein_input.send_keys("15")

        # Enviar el formulario
        submit_button.click()

        # Esperar a que se cierre el formulario y verificar que la tabla de platos está visible
        DishesLocators.DATA_TABLE.wait_until_visible(self.driver)

    @add_test_info(
        description="Verificar que el plato es visible en la tabla después de agregarlo",
        expected_result="El plato debe aparecer en la tabla de platos",
        module="UI",
        test_id="DISHES-UI-003",
    )
    @pytest.mark.order(9)
    def test_dish_appears_in_table(self):
        """Verificar que el plato agregado aparece en la tabla"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/dishes")

        # Verificar que la tabla de platos está presente
        DishesLocators.DATA_TABLE.wait_until_visible(self.driver)

        # Verificar que hay al menos una fila en la tabla
        rows = DishesLocators.DATA_TABLE_ROWS.find_elements(self.driver)
        assert len(rows) > 0, "No hay platos en la tabla"

    @add_test_info(
        description="Verificar funcionalidad de validación del formulario de platos",
        expected_result="El formulario debe mostrar errores cuando los campos requeridos están vacíos",
        module="UI",
        test_id="DISHES-UI-004",
    )
    @pytest.mark.order(10)
    def test_dish_form_validation(self):
        """Verificar validación del formulario de platos"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/dishes")

        # Hacer clic en el botón de agregar plato
        DishesLocators.ADD_DISH_BTN.wait_until_present(self.driver)
        add_button = DishesLocators.ADD_DISH_BTN.find_element(self.driver)
        add_button.click()

        # Verificar que se abre el formulario de creación de plato
        DishesLocators.DISH_FORM_TITLE.wait_until_present(self.driver)

        # Limpiar campos obligatorios
        dish_name_input = DishesLocators.DISH_NAME_INPUT.find_element(self.driver)
        dish_description_input = DishesLocators.DISH_DESCRIPTION_INPUT.find_element(
            self.driver
        )
        dish_name_input.clear()
        dish_description_input.clear()

        # Enviar el formulario sin completar los campos obligatorios
        submit_button = DishesLocators.DISH_FORM_SUBMIT_BTN.find_element(self.driver)
        submit_button.click()

        # Verificar que se muestran errores de validación
        error_messages = self.driver.find_elements(By.CSS_SELECTOR, ".text-red-500")
        assert (
            len(error_messages) > 0
        ), "No se mostraron mensajes de error de validación"

    @add_test_info(
        description="Verificar que los botones de activar/desactivar platos funcionan correctamente",
        expected_result="Los botones de activar/desactivar deben cambiar el estado del plato",
        module="UI",
        test_id="DISHES-UI-005",
    )
    @pytest.mark.order(11)
    def test_toggle_dish_active_state(self):
        """Verificar que los botones de activar/desactivar funcionan correctamente"""
        self.driver.get(f"{settings.BASE_FRONTEND_URL}/menu/dishes")

        # Verificar que la tabla de platos está presente
        DishesLocators.DATA_TABLE.wait_until_visible(self.driver)

        # Verificar que hay al menos una fila en la tabla
        rows = DishesLocators.DATA_TABLE_ROWS.find_elements(self.driver)
        assert len(rows) > 0, "No hay platos en la tabla"

        # Abrir las acciones del primer plato
        DishesLocators.DATA_TABLE_ACTION_OPEN_BTN.wait_until_visible(self.driver)
        action_buttons = DishesLocators.DATA_TABLE_ACTION_OPEN_BTN.find_elements(
            self.driver
        )
        assert len(action_buttons) > 0, "No se encontraron botones de acción"
        action_buttons[0].click()

        # Verificar que el botón de desactivar está presente
        DishesLocators.ACTION_DISABLE_BUTTON.wait_until_visible(self.driver)
        DishesLocators.ACTION_DISABLE_BUTTON.wait_until_clickable(self.driver)
        disable_button = DishesLocators.ACTION_DISABLE_BUTTON.find_element(self.driver)
        assert disable_button.is_displayed(), "Botón de desactivar no visible"

        # Hacer clic en el botón de desactivar
        disable_button.click()

        # Esperar a que aparezca el modal de confirmación
        DishesLocators.DISABLE_CONFIRMATION_MODAL.wait_until_visible(self.driver)

        # Confirmar la desactivación
        confirm_button = DishesLocators.DISABLE_CONFIRMATION_MODAL_BUTTON.find_element(
            self.driver
        )
        confirm_button.click()

        # Esperar a que se cierre el modal y verificar que el plato está desactivado
        DishesLocators.DISABLE_CONFIRMATION_MODAL.wait_until_invisible(self.driver)

        # Recargar la página para verificar el estado del plato
        self.driver.refresh()
        DishesLocators.DATA_TABLE.wait_until_visible(self.driver)

        # Verificar que el estado del plato ha cambiado (debería estar desactivado)
        rows = DishesLocators.DATA_TABLE_ROWS.find_elements(self.driver)
        assert len(rows) > 0, "No hay platos en la tabla después de recargar"
