import time

from .base import BaseNavigator

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TrNavigator(BaseNavigator):
    def __init__(self, url: str):
        """Initializes the TrNavigator with a Firefox driver."""
        super().__init__(url=url)

    def get_shadow_root(self, element):
        """A helper function to get the shadow root of a web element."""
        return self.driver.execute_script('return arguments[0].shadowRoot', element)

    def get_keyboard_container(self):
        """Navigates through the nested Shadow DOM to find the keyboard container."""
        game_app = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "game-app")))
        game_app_shadow_root = self.get_shadow_root(game_app)

        game_keyboard = WebDriverWait(game_app_shadow_root, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "game-keyboard")))
        keyboard_shadow_root = self.get_shadow_root(game_keyboard)

        keyboard_container = WebDriverWait(keyboard_shadow_root, 15).until(EC.presence_of_element_located((By.ID, "keyboard")))
        return keyboard_container

    def type_word(self, word_to_type: str):
        """Finds the virtual keyboard and types the given word."""
        print(f"Attempting to type the word: {word_to_type}")

        keyboard_container = self.get_keyboard_container()
        tr_translator = str.maketrans("ÖÜĞŞİÇ", "öüğşiç")
        word_to_type = word_to_type.translate(tr_translator)
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

        try:
            # 1. Get the top-level game-app and its shadow root
            game_app = self.driver.find_element(By.TAG_NAME, 'game-app')
            game_app_shadow_root = self.get_shadow_root(game_app)

            game_div = WebDriverWait(game_app_shadow_root, 10).until(
                EC.presence_of_element_located((By.ID, 'game'))
            )
            board_container = WebDriverWait(game_div, 10).until(
                EC.presence_of_element_located((By.ID, 'board-container'))
            )
            board = WebDriverWait(board_container, 10).until(
                EC.presence_of_element_located((By.ID, 'board'))
            )

            # 4. Now we are in the correct context to find the row
            row_selector = f"game-row:nth-of-type({attempt_index + 1})"
            row_element = WebDriverWait(board, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, row_selector))
            )

            # 5. Wait for the evaluation to be complete on the last tile of that row.
            row_shadow_root = self.get_shadow_root(row_element)
            last_tile_selector = "game-tile:nth-of-type(5)"
            last_tile = WebDriverWait(row_shadow_root, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, last_tile_selector))
            )

            # The final and most reliable wait: wait until the 'evaluation' attribute is not null.
            WebDriverWait(self.driver, 5).until(
                lambda d: last_tile.get_attribute("evaluation") is not None
            )

        except TimeoutException as e:
            print(e)
            print("Error: Timed out waiting for row evaluation. The word was likely invalid.")
            return "INVALID"

        # If we get here, the word was valid and animation is complete.
        feedback = []
        # We already have the row element from the wait, and its shadow root
        tiles = row_shadow_root.find_elements(By.CSS_SELECTOR, "game-tile")

        for tile in tiles:
            status = tile.get_attribute("evaluation")
            if status == "correct":
                feedback.append("G")
            elif status == "present":
                feedback.append("Y")
            else: # status == "absent"
                feedback.append("B")
                
        result = "".join(feedback)
        print(f"Result found: {result}")
        return result

    def read_final_result(self, history: list) -> str:
        """Reads the final result (colors) from the last row after all guesses."""
        print("Reading final result...")
        try:
            time.sleep(1)

            # 1. Get the top-level game-app and its shadow root
            game_app = self.driver.find_element(By.TAG_NAME, "game-app")
            game_app_shadow_root = self.get_shadow_root(game_app)

            game_div = WebDriverWait(game_app_shadow_root, 10).until(
                EC.presence_of_element_located((By.ID, "game"))
            )
            # find the game-stats element
            game_modal = game_div.find_element(By.TAG_NAME, "game-modal")
            game_stats = game_modal.find_element(By.TAG_NAME, "game-stats")
            game_stats_shadow_root = self.get_shadow_root(game_stats)

            # get the share button
            share_button = WebDriverWait(game_stats_shadow_root, 10).until(
                EC.presence_of_element_located((By.ID, "share-button"))
            )
            if share_button:
                share_button.click()

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
        print("Setting up the navigator for TR Wordle...")
        super().setup()
        self.driver.get(self.url)
        self.get_keyboard_container()
        print("Game keyboard loaded.")
        try:
            game_app = self.driver.find_element(By.TAG_NAME, 'game-app')
            game_app_shadow_root = self.get_shadow_root(game_app)
            close_icon = WebDriverWait(game_app_shadow_root, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.close-icon'))
            )
            print("Closing the help pop-up.")
            close_icon.click()
            time.sleep(1)
        except TimeoutException:
            print("Help pop-up not found or already closed.")

        # type a dummy letter to avoid missing the first letter in the first guess
        self.type_word("A")
        time.sleep(0.5)
        self.clear_word(1)
        time.sleep(0.5)
