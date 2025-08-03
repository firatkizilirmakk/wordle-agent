import time
import argparse

from navigator.tr_navigator import TrNavigator
from navigator.en_navigator import EnNavigator

from agents.tr_agent import TrAgent
from agents.en_agent import EnAgent

def run(language: str, **kwargs):
    """Runs the Wordle bot for the specified language."""
    if language == "en":
        url = "https://www.nytimes.com/games/wordle/index.html"
        navigator = EnNavigator(url=url)
        agent = EnAgent()
    elif language == "tr":
        url = "https://wordleturkce.bundle.app/"
        navigator = TrNavigator(url=url)
        agent = TrAgent()

    history = []
    won = False
    for i in range(6): 
        current_attempt = i
        while True:
            guess = agent.get_ai_guess(history)
            if len(guess) != 5:
                history.append({"guess": guess, "feedback": "INVALID"})
                continue

            navigator.type_word(guess)
            time.sleep(5) 

            feedback = navigator.read_result(current_attempt)
            if feedback == "INVALID":
                history.append({"guess": guess, "feedback": "INVALID"})
                navigator.clear_word(len(guess))
            else:
                history.append({"guess": guess, "feedback":feedback})
                break

        if feedback == "GGGGG":
            won = True
    if won:
        print(f"SUCCESS! The word was '{guess}'. Solved in {current_attempt + 1} attempts.")
    else:
        print("FAILED! Could not solve in 6 attempts.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wordle Bot")
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        choices=["en", "tr"],
        default="en",
        help="Language to play Wordle in (en/tr)",
    )
    args = parser.parse_args()
    run(args.language)
