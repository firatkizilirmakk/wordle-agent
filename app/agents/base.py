import os
from dotenv import load_dotenv

import openai

load_dotenv()
API_KEY = os.environ.get("OPENAI_API_KEY")

class BaseAgent:
    """Base class for all agents in the application."""
    
    def __init__(self):
        """Initializes the BaseAgent"""
        try:
            self.client = openai.OpenAI(api_key=API_KEY)
        except Exception as e:
            print(f"Failed to initialize OpenAI client: {e}")
            raise e

    def get_historic_state(self, history: list) -> dict:
        """Retrieves the historic and current state of the game."""
        green_letters = {}
        gray_letters = set()
        all_yellows = set()

        for turn in history:
            guess, feedback = turn["guess"], turn["feedback"]
            if feedback in ["INVALID", "INVALID_REPEATED", "INVALID_LENGTH"]:
                continue
            for i, letter in enumerate(guess):
                if feedback[i] == "G":
                    green_letters[i] = letter
                    if letter in gray_letters:
                        gray_letters.remove(letter)
                elif feedback[i] == "Y":
                    all_yellows.add(letter)
                elif feedback[i] == "B":
                    if letter not in green_letters.values() and letter not in all_yellows:
                        gray_letters.add(letter)

        # This prevents telling the AI contradictory information.
        final_yellows = all_yellows - set(green_letters.values())

        return {
            "green_letters": green_letters,
            "gray_letters": gray_letters,
            "yellow_letters": final_yellows
        }

    def get_ai_guess(self, history: list) -> str:
        """Generates a guess using the AI client based on the history of attempts."""
        raise NotImplementedError("Subclasses must implement this method.")

    def _get_user_prompt(self, history: list) -> str:
        """Generates the user prompt for the AI based on the game history."""
        raise NotImplementedError("Subclasses must implement this method.")