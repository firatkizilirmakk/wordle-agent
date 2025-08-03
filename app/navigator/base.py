from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

GECKODRIVER_PATH = "./geckodriver"

class BaseNavigator:
    def __init__(self, url: str):
        """Initializes the BaseNavigator with a Firefox driver."""
        self.url = url
        self.setup()

    def setup_driver(self):
        """Sets up the Firefox driver for Selenium."""
        print("Setting up Firefox driver...")
        firefox_options = Options()
        # firefox_options.add_argument("--headless") 
        service = Service(executable_path=GECKODRIVER_PATH)
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.set_page_load_timeout(30)
        return driver

    def get_keyboard_container(self):
        """Finds the keyboard container for the current game."""
        raise NotImplementedError("Subclasses must implement this method.")

    def type_word(self, word_to_type: str):
        """Types the given word using the virtual keyboard."""
        raise NotImplementedError("Subclasses must implement this method.")

    def clear_word(self, length: int):
        """Clears the specified number of letters from the grid."""
        raise NotImplementedError("Subclasses must implement this method.")

    def read_result(self, attempt_index: int) -> str:
        """Reads the result (colors) from a specific row after a guess."""
        raise NotImplementedError("Subclasses must implement this method.")

    def setup(self):
        """Sets up the navigator."""
        self.driver = self.setup_driver()
