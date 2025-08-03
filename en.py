import time
import openai
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# --- NYT Wordle Configuration ---
OPENAI_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your OpenAI API key
GECKODRIVER_PATH = './geckodriver'
WORDLE_URL = "https://www.nytimes.com/games/wordle/index.html"

# --- Selenium Helper Functions ---

def setup_driver():
    """Sets up the Firefox driver for Selenium."""
    print("Setting up Firefox driver for NYT Wordle...")
    firefox_options = Options()
    # firefox_options.add_argument("--headless") 
    service = Service(executable_path=GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.set_page_load_timeout(30)
    return driver

def get_keyboard_container(driver):
    """Finds the keyboard container for NYT Wordle."""
    return WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class^="Keyboard-module_keyboard"]')))

def type_word(driver, word_to_type: str):
    """Finds the virtual keyboard and types the given word."""
    print(f"Attempting to type the word: {word_to_type}")
    keyboard_container = get_keyboard_container(driver)
    
    for letter in word_to_type:
        key_element = keyboard_container.find_element(By.CSS_SELECTOR, f"button[data-key='{letter.lower()}']")
        key_element.click()
        time.sleep(0.4) 

    enter_key = keyboard_container.find_element(By.CSS_SELECTOR, "button[data-key='↵']")
    enter_key.click()
    print("Word typed and submitted.")

def clear_word(driver, length: int):
    """Clicks the backspace key to clear an invalid word from the grid."""
    print(f"Clearing {length} letter(s) from the grid...")
    keyboard_container = get_keyboard_container(driver)
    backspace_key = keyboard_container.find_element(By.CSS_SELECTOR, "button[data-key='←']")
    for _ in range(length):
        backspace_key.click()
        time.sleep(0.05)

def read_result(driver, attempt_index: int) -> str:
    """Reads the result (colors) from a specific row after a guess."""
    print(f"Reading result for attempt {attempt_index + 1}...")

    tiles = []
    try:
        # 1. Find the main game container
        game_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'wordle-app-game'))
        )

        # 2. Find the board element within the game container
        board = game_container.find_element(By.CSS_SELECTOR, 'div[class^="Board-module_board"]')
        
        # 3. Get all rows within the board
        rows = board.find_elements(By.CSS_SELECTOR, 'div[class^="Row-module_row"]')
        row_element = rows[attempt_index]

        # --- FIX: Account for the intermediate div between the row and the tiles ---
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

# --- AI Logic Functions ---

def get_ai_guess(client, history: list) -> str:
    """Calls the OpenAI API to get the next best guess with improved logic."""
    print("\nAsking OpenAI for the next English guess...")

    green_letters, yellow_letters, gray_letters, all_yellows, previous_guesses = {}, defaultdict(set), set(), set(), [t['guess'] for t in history]
    for turn in history:
        guess, feedback = turn['guess'], turn['feedback']
        if feedback in ['INVALID', 'INVALID_REPEATED', 'INVALID_LENGTH']:
            continue
        for i, letter in enumerate(guess):
            if feedback[i] == 'G':
                green_letters[i] = letter
                if letter in gray_letters:
                    gray_letters.remove(letter)
            elif feedback[i] == 'Y':
                yellow_letters[i].add(letter)
                all_yellows.add(letter)
            elif feedback[i] == 'B':
                if letter not in green_letters.values() and letter not in all_yellows:
                    gray_letters.add(letter)
    final_yellows = all_yellows - set(green_letters.values())

    system_prompt = """You are an expert English Wordle solver. You will be given the game state and a list of rules. Your goal is to provide the single best 5-letter English word as a guess.

Here is an example of how to think:
--- EXAMPLE ---
GAME STATE:

    Guess: SLATE, Result: YBYBB
    Guess: MARSH, Result: BGGGG

B stands for gray, Y stands for yellow, and G stands for green.
Gray means the letter is not in the word, yellow means it is in the word but not in that position, and green means it is in the correct position.

ANALYSIS:

    1. From SLATE, I know 'S' and 'A' are yellow. They are in the word, but 'S' is not in position 1 and 'A' is not in position 3.
    2. 'L', 'T', 'E' are gray. They are not in the word.
    3. For the next guess, I need a word that contains 'S' and 'A' in new positions and does not contain 'L', 'T', 'E'.
    4. I will predict MARSH.
    5. From MARSH, I know 'A' is the 2nd letter, 'R' is the 3rd, 'S' is the 4th, and 'H' is the 5th. The word is _ARSH.
    6. 'M' is gray. It is not in the word.
    7. Up to this point, I have deduced the word is _ARSH and does not contain L, T, E, M.
    8. A logical next guess to discover the first letter would be TRASH or CRASH. I will predict TRASH.

--- END EXAMPLE ---

You must follow this logical process. Your response MUST be a single 5-letter English word and nothing else.
"""

    user_prompt = "Here is the current game state. Follow the example and provide the next best guess.\n\n"
    user_prompt += "--- CURRENT GAME STATE ---\n"

    if not history:
        user_prompt += "This is the first guess. A good starting word is 'ARISE' or 'SLATE'.\n"
    else:
        for turn in history:
            user_prompt += f"Guess: {turn['guess']}, Result: {turn['feedback']}\n"

    user_prompt += "\n--- RULES YOU MUST FOLLOW ---\n"
    if green_letters:
        rule = ["_"] * 5
        for pos, letter in green_letters.items():
            rule[pos] = letter
        user_prompt += f"- The word MUST match this pattern: {''.join(rule)}\n"
    if final_yellows:
        user_prompt += f"- The word **MUST** contain '{', '.join(sorted(list(final_yellows)))}'. Look up the history and find proper placements for them.\n"
    if gray_letters:
        user_prompt += f"- The word **MUST NOT** contain these letters: {', '.join(sorted(list(gray_letters)))}\n"
    if previous_guesses:
        user_prompt += f"- **DO NOT** use these words again: {', '.join(previous_guesses)}\n\n"

    user_prompt += "---\n\n_You are now operating under these rules. Follow them in all future responses._\nYour single best 5-letter ENGLISH guess:"

    print("User prompt", user_prompt)
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.2, max_tokens=10)
        ai_word = response.choices[0].message.content.strip().upper().replace(" ", "")
        ai_word_sanitized = "".join([c for c in ai_word if c.isalpha()]).upper()
        if len(ai_word_sanitized) > 5:
            ai_word_sanitized = ai_word_sanitized[:5]
        print(f"AI suggested: {ai_word_sanitized}")
        return ai_word_sanitized
    except Exception as e:
        print(f"An error occurred with the OpenAI API: {e}")
        return "ARISE"

def main():
    """Main function to run the fully autonomous Wordle solver."""
    print("--- Autonomous NYT Wordle Solver (OpenAI) ---")
    if OPENAI_API_KEY == "YOUR_API_KEY_HERE" or not OPENAI_API_KEY:
        print("ERROR: Please paste your OpenAI API Key into the script.")
        return
    try:
        ai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized.")
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        return
    driver = setup_driver()
    history = []
    try:
        driver.get(WORDLE_URL)
        print("Waiting for the game to load...")
        try:
            play_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="Play"]')))
            print("Found initial 'Play' button. Clicking it.")
            play_button.click()
            time.sleep(1)
        except TimeoutException:
            print("'Play' button not found, assuming we are already on the game screen.")

        # Close pop-up
        try:
            close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="icon-close"]')))
            print("Closing the help pop-up.")
            close_button.click()
            time.sleep(1)
        except TimeoutException:
            print("Help pop-up not found or already closed.")
        
        get_keyboard_container(driver)
        print("Game keyboard loaded.")
        
        # Wake-up keystroke is always a good idea
        print("Performing a 'wake-up' keystroke to activate the input...")
        type_word(driver, "A")
        time.sleep(0.5)
        clear_word(driver, 1)
        time.sleep(0.5)
        print("Wake-up complete.")

        for i in range(6): 
            current_attempt = i
            print("-" * 30)
            print(f"--- Attempt {current_attempt + 1} ---")
            while True: 
                guess = get_ai_guess(ai_client, history)
                if guess in [turn['guess'] for turn in history]:
                    print(f"AI repeated a guess ('{guess}'). Asking for a new one.")
                    history.append({'guess': guess, 'feedback': 'INVALID_REPEATED'})
                    continue
                if len(guess) != 5:
                    history.append({'guess': guess, 'feedback': 'INVALID_LENGTH'})
                    continue 
                type_word(driver, guess)
                time.sleep(3) 
                feedback = read_result(driver, current_attempt)
                if feedback == "INVALID":
                    history.append({'guess': guess, 'feedback': 'INVALID'})
                    clear_word(driver, len(guess))
                else:
                    history.append({'guess': guess, 'feedback':feedback})
                    break 
            if feedback == "GGGGG":
                print(f"\nSUCCESS! The word was '{guess}'. Solved in {current_attempt + 1} attempts.")
                break
        else: 
            print("\nFAILURE. Could not solve the puzzle in 6 attempts.")
        print("\nGame finished. The browser will close in 20 seconds.")
        time.sleep(20)
    except WebDriverException as e:
        print(f"A browser error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Closing browser.")
        driver.quit()

if __name__ == "__main__":
    main()
