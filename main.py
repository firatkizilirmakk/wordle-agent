import os
import time
from collections import defaultdict

from dotenv import load_dotenv
import openai

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

load_dotenv()

# --- Configuration ---
API_KEY = os.environ.get("OPENAI_API_KEY") 

GECKODRIVER_PATH = './geckodriver' 
WORDLE_URL = "https://wordleturkce.bundle.app/"

# --- Selenium Helper Functions ---

def get_shadow_root(driver, element):
    """A helper function to get the shadow root of a web element."""
    return driver.execute_script('return arguments[0].shadowRoot', element)

def setup_driver():
    """Sets up the Firefox driver for Selenium."""
    print("Setting up Firefox driver...")
    firefox_options = Options()
    # firefox_options.add_argument("--headless") 
    service = Service(executable_path=GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.set_page_load_timeout(30)
    return driver

def get_keyboard_container(driver):
    """Navigates through the nested Shadow DOM to find the keyboard container."""
    game_app = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'game-app')))
    game_app_shadow_root = get_shadow_root(driver, game_app)
    
    game_keyboard = WebDriverWait(game_app_shadow_root, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'game-keyboard')))
    keyboard_shadow_root = get_shadow_root(driver, game_keyboard)
    
    keyboard_container = WebDriverWait(keyboard_shadow_root, 15).until(EC.presence_of_element_located((By.ID, 'keyboard')))
    return keyboard_container

def type_word(driver, word_to_type: str):
    """Finds the virtual keyboard and types the given word."""
    print(f"Attempting to type the word: {word_to_type}")
    
    keyboard_container = get_keyboard_container(driver)

    tr_translator = str.maketrans("ÖÜĞŞİÇ", "öüğşiç")
    word_to_type = word_to_type.translate(tr_translator)
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
    
    try:
        # --- FIX: Accurately navigate the full nested structure based on the user's layout.png ---
        # 1. Get the top-level game-app and its shadow root
        game_app = driver.find_element(By.TAG_NAME, 'game-app')
        game_app_shadow_root = get_shadow_root(driver, game_app)
      
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
        row_shadow_root = get_shadow_root(driver, row_element)
        last_tile_selector = "game-tile:nth-of-type(5)"
        last_tile = WebDriverWait(row_shadow_root, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, last_tile_selector))
        )

        # The final and most reliable wait: wait until the 'evaluation' attribute is not null.
        WebDriverWait(driver, 5).until(
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

# --- AI Logic Functions ---
# --- FIX 2: Major upgrade to the AI prompting logic ---
def get_ai_guess(client, history: list) -> str:
    """Calls the OpenAI API to get the next best guess with improved logic."""
    print("\nAsking OpenAI for the next guess...")

    # Analyze history to create a summary of known letters
    green_letters = {}  # {position: letter}
    yellow_letters = defaultdict(set)  # {position: {letters}}
    gray_letters = set()
    all_yellows = set()

    for turn in history:
        guess = turn['guess']
        feedback = turn['feedback']
        if feedback == 'INVALID':
            continue
        for i, letter in enumerate(guess):
            if feedback[i] == 'G':
                green_letters[i] = letter
                if letter in gray_letters:
                    gray_letters.remove(letter) # A letter can be green even if grayed out before
            elif feedback[i] == 'Y':
                yellow_letters[i].add(letter)
                all_yellows.add(letter)
            elif feedback[i] == 'B':
                # Only add to gray if it's not green or yellow anywhere
                if letter not in green_letters.values() and letter not in all_yellows:
                    gray_letters.add(letter)

    # Build a detailed prompt with explicit rules
    system_prompt = "You are an expert Turkish Wordle solver. Your goal is to find the secret 5-letter word. You must follow all rules derived from the guess history."
    
    user_prompt = "Here is the current state of the game:\n"
    
    # Add rules based on our analysis
    if green_letters:
        rule = ["_"] * 5
        for pos, letter in green_letters.items():
            rule[pos] = letter
        user_prompt += f"- The word so far: {''.join(rule)}\n"
    if all_yellows:
        user_prompt += f"- The word MUST contain the letter(s): {', '.join(sorted(list(all_yellows)))}\n"
    if yellow_letters:
        for pos, letters in yellow_letters.items():
            user_prompt += f"- The letter at position {pos+1} CANNOT be: {', '.join(sorted(list(letters)))}\n"
    if gray_letters:
        user_prompt += f"- The word MUST NOT contain the letter(s): {', '.join(sorted(list(gray_letters)))}\n"

    user_prompt += "\nPrevious Guesses:\n"
    if not history:
        user_prompt += "None yet. Provide the best starting word. A good starting word is 'EKRAN' or 'ARABA'.\n"
    else:
        for turn in history:
            user_prompt += f"- {turn['guess']}: {turn['feedback']}\n"
    
    user_prompt += "\nBased on all these rules, provide your next best guess. Your response must be ONLY the single 5-letter word."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    print("Sending request to OpenAI API...")
    print("Prompt sent:", messages)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3, # Lower temperature for more logical output
            max_tokens=10
        )
        ai_word = response.choices[0].message.content.strip().upper().replace(" ", "")
        ai_word_sanitized = "".join([c for c in ai_word if c.isalpha()]).upper()
        if len(ai_word_sanitized) > 5:
            ai_word_sanitized = ai_word_sanitized[:5]
        
        print(f"AI suggested: {ai_word_sanitized}")
        return ai_word_sanitized
    except Exception as e:
        print(f"An error occurred with the OpenAI API: {e}")
        return "MERAK"

def main():
    """Main function to run the fully autonomous Wordle solver."""
    print("--- Autonomous Turkish Wordle Solver (OpenAI) ---")

    try:
        ai_client = openai.OpenAI(api_key=API_KEY)
        print("OpenAI client initialized.")
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        return
    driver = setup_driver()
    history = []
    try:
        driver.get(WORDLE_URL)
        print("Waiting for the game to load...")
        get_keyboard_container(driver)
        print("Game keyboard loaded.")
        try:
            game_app = driver.find_element(By.TAG_NAME, 'game-app')
            game_app_shadow_root = get_shadow_root(driver, game_app)
            close_icon = WebDriverWait(game_app_shadow_root, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.close-icon')))
            print("Closing the help pop-up.")
            close_icon.click()
            time.sleep(1)
        except TimeoutException:
            print("Help pop-up not found or already closed.")
        
        # --- FIX 1: "Wake-up" keystroke to prevent mistyped first word ---
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
                if len(guess) != 5:
                    history.append({'guess': guess, 'feedback': 'INVALID'})
                    continue 
                type_word(driver, guess)
                time.sleep(5) 
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
