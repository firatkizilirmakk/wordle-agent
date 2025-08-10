import time

from .base import BaseNavigator

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class EnNavigator(BaseNavigator):
    def __init__(self, url: str):
        """Initializes the EnNavigator with a Firefox driver."""
        super().__init__(url=url)

    def get_keyboard_container(self):
        """Finds the keyboard container for English Wordle."""
        return WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class^="Keyboard-module_keyboard"]'))
        )

    def type_word(self, word_to_type: str):
        """Finds the virtual keyboard and types the given word."""
        print(f"Attempting to type the word: {word_to_type}")
        keyboard_container = self.get_keyboard_container()

        for letter in word_to_type:
            key_element = keyboard_container.find_element(By.CSS_SELECTOR, f"button[data-key='{letter.lower()}']")
            key_element.click()
            time.sleep(0.4) 

        enter_key = keyboard_container.find_element(By.CSS_SELECTOR, "button[data-key='↵']")
        enter_key.click()
        print("Word typed and submitted.")

    def clear_word(self, length: int):
        """Clicks the backspace key to clear an invalid word from the grid."""
        print(f"Clearing {length} letter(s) from the grid...")
        keyboard_container = self.get_keyboard_container()
        backspace_key = keyboard_container.find_element(By.CSS_SELECTOR, "button[data-key='←']")
        for _ in range(length):
            backspace_key.click()
            time.sleep(0.05)

    def read_result(self, attempt_index: int) -> str:
        """Reads the result (colors) from a specific row after a guess."""
        print(f"Reading result for attempt {attempt_index + 1}...")

        tiles = []
        try:
            # 1. Find the main game container
            game_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'wordle-app-game'))
            )

            # 2. Find the board element within the game container
            board = game_container.find_element(By.CSS_SELECTOR, 'div[class^="Board-module_board"]')
            
            # 3. Get all rows within the board
            rows = board.find_elements(By.CSS_SELECTOR, 'div[class^="Row-module_row"]')
            row_element = rows[attempt_index]

            # 4. Find the container of the tiles, which is the direct child of the row
            tile_container = row_element.find_elements(By.CSS_SELECTOR, 'div[class=""]')
            for container in tile_container:
                # 7. Now that evaluation is complete, get all tiles from the tile container
                tile = container.find_elements(By.CSS_SELECTOR, 'div[data-testid="tile"]')
                tiles.append(tile[0])  # Each tile is a single div element
        except TimeoutException:
            print("Error: Timed out waiting for row evaluation. The word was likely invalid.")
            return "INVALID"

        feedback = []
        for tile in tiles:
            # NYT uses 'correct', 'present', 'absent' in the 'data-state' attribute
            status = tile.get_attribute("data-state")
            if status == "correct":
                feedback.append("G")
            elif status == "present":
                feedback.append("Y")
            elif status == "absent":
                feedback.append("B")
            elif status == "tbd":
                return "INVALID"  # If the tile is still being evaluated, return INVALID

        result = "".join(feedback)
        print(f"Result found: {result}")
        return result

    def read_final_result(self, history: list) -> str:
        """reads the final result of the game."""
        try:
            time.sleep(1)  # Wait for the game to finish processing
            first_close_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class^="Modal-module_closeIconButton"]'))
            )
            if first_close_button:
                first_close_button.click()

            time.sleep(1)  # Wait for the modal to close
            button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class^="Footer-module_shareButton"]'))
            )
            if button:
                button.click()

            time.sleep(1)  # Wait for the share modal to open
            try:
                return self.driver.execute_script("return navigator.clipboard.readText();")
            except Exception as e:
                print(f"Error reading clipboard: {e}")
                return self._get_shareable_output(history)
        except TimeoutException:
            print("Final result button not found, assuming the game is still ongoing.")
            return None

    def setup(self):
        """Sets up the navigator."""
        print("Setting up the EnNavigator...")
        super().setup()
        self.driver.get(self.url)

        # entering with the play button
        try:
            play_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="Play"]')))
            print("Found initial 'Play' button. Clicking it.")
            play_button.click()
            time.sleep(1)
        except TimeoutException:
            print("'Play' button not found, assuming we are already on the game screen.")

        # Close pop-up
        try:
            close_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="icon-close"]')))
            print("Closing the help pop-up.")
            close_button.click()
            time.sleep(1)
        except TimeoutException:
            print("Help pop-up not found or already closed.")

        self.get_keyboard_container()
        print("Game keyboard loaded.")

        # Wake-up keystroke is always a good idea
        self.type_word("A")
        time.sleep(0.5)
        self.clear_word(1)
        time.sleep(0.5)
