from selenium import webdriver
from seleniumpagefactory.Pagefactory import PageFactory  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait


class BasePage(PageFactory):
    """
    Base class for all page objects in the UI tests.
    Provides common functionality that can be shared across different page objects.
    """

    MAX_WAIT_TIME_IN_SECONDS = 10

    def __init__(self, driver: webdriver.Chrome | webdriver.Firefox):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, self.MAX_WAIT_TIME_IN_SECONDS)

    # Define locators for common elements
    locators = {
        "toogleSidebarBtn": ("CSS", "#sidebar-toggle-btn"),
        "sidebarHomeLink": ("CSS", "#sidebar-menu li a"),
        "sidebarElementsList": ("CSS", "#sidebar-menu li button"),
    }

    def wait_element_visible(self, element_name: str):
        """
        Wait for an element to be visible on the page.
        :param element_name: The name of the element to wait for.
        """
        self.wait.until(lambda driver: self.is_element_visible(element_name))

    def wait_elements_visible(self, element_name_list: list[str]):
        """
        Wait for multiple elements to be visible on the page.
        :param element_name_list: List of element names to wait for.
        """
        for element_name in element_name_list:
            self.wait_element_visible(element_name)

    def toggle_sidebar(self):
        """
        Click the toggle sidebar button to show or hide the sidebar.
        """
        self.toogleSidebarBtn.click()

    def go_to_home(self):
        """
        Navigate to the home page by clicking the sidebar home link.
        """
        self.sidebarHomeLink.click()

    def get_sidebar_elements(self):
        """
        Get a list of all sidebar elements.
        :return: List of sidebar element WebElements.
        """
        return self.sidebarElementsList.find_elements()

    def maximize_window(self):
        """
        Maximize the browser window.
        """
        self.driver.maximize_window()
