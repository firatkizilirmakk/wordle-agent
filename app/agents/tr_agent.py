from .base import BaseAgent

class TrAgent(BaseAgent):
    """TR Wordle Agent"""

    def __init__(self):
        super().__init__()
        self.system_prompt = """
        You are an expert Turkish Wordle solver. You will be given the game state and a list of rules. Your goal is to provide the single best 5-letter Turkish word as a guess.
        Here is an example of how to think:
        --- EXAMPLE ---
        GAME STATE:

        - Guess: TENIS, Result: BBYBY
        - Guess: SABUN, Result: GBBGG
        - Guess: SOMUN, Result: GGBGG
        - Guess: SORUN, Result: GGGGG

        B stands for gray, Y stands for yellow, and G stands for green.
        Gray means the letter is not in the word, yellow means it is in the word but not in that position, and green means it is in the correct position.

        ANALYSIS:
        1. From TENIS, I know 'T', 'E', 'İ' are gray. They are not in the word.
        2. 'N' and 'S' are yellow, meaning they are in the word but not in those positions.
        So, 'N' must be in positions 1, 2, 4, or 5, and 'S' must be in positions 1, 2, 3, or 4.
        Therefore, for the next guess, I will avoid 'T', 'E', 'İ' and insert 'N' and 'S' in new positions.
        3. Predicting SABUN as I need to use 'S' and 'N' in new positions.
        4. From SABUN, I know 'S' is the 1st letter, 'U' is the 4th letter and 'N' is the 5th letter. The word is S__UN.
        5. 'A', 'B' are gray. They are not in the word.
        6. From SOMUN, I know 'O' is in the 2nd position. The word is SO_UN.
        7. 'M' is gray (B). It is not in the word.
        8. Up to this point, I have deduced the word is SO_UN and does not contain T, E, İ, A, B, M.
        9. Then, I predict the word as SORUN, which is correct.

        --- END EXAMPLE ---

        You must follow this logical process. Your response MUST be a single 5-letter Turkish word and nothing else.
        """

    def _get_user_prompt(self, history: list) -> str:
        """Generates the user prompt for the AI based on the game history."""
        previous_guesses = [turn["guess"] for turn in history]
        state = self.get_historic_state(history)
        green_letters, gray_letters, final_yellows = state["green_letters"], state["gray_letters"], state["yellow_letters"]

        user_prompt = "Here is the current game state. Follow the example and provide the next best guess.\n\n"
        user_prompt += "--- CURRENT GAME STATE ---\n"

        if not history:
            user_prompt += "This is the first guess. A good starting word is 'selam' or 'merak'.\n"
        else:
            for turn in history:
                user_prompt += f"Guess: {turn['guess']}, Result: {turn['feedback']}\n"
        
        user_prompt += "\n--- RULES YOU MUST FOLLOW ---\n"
        if green_letters:
            rule = ["_"] * 5
            for pos, letter in green_letters.items():
                rule[pos] = letter
            user_prompt += f"- The word **MUST** match this pattern: {''.join(rule)}\n"
        if final_yellows:
            user_prompt += f"- The word **MUST** contain '{', '.join(sorted(list(final_yellows)))}'. Look up the history and find proper placements for them.\n"
        if gray_letters:
            user_prompt += f"- The word **MUST NOT** contain these letters: {', '.join(sorted(list(gray_letters)))}\n"
        if previous_guesses:
            user_prompt += f"- **DO NOT** use these words again ever: {', '.join(previous_guesses)}\n\n"
        user_prompt += "You must follow these rules strictly. Do not break them.\n"

        user_prompt += "---\n\n_You are now operating under these rules. Follow them in all future responses._\nYour next best 5-letter TURKISH guess:"
        return user_prompt

    def get_ai_guess(self, history: list) -> str:
        """Generates a guess using the AI client based on the history of attempts."""
        user_prompt = self._get_user_prompt(history)
        messages = [{"role": "system", "content": self.system_prompt}, {"role": "user", "content": user_prompt}]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.2,
                max_tokens=10
            )
            ai_word = response.choices[0].message.content.strip().replace(" ", "")
            if len(ai_word) > 5:
                ai_word = ai_word[:5]

            print(f"AI suggested: {ai_word}")
            return ai_word
        except Exception as e:
            print(f"An error occurred with the OpenAI API: {e}")
            return "MERAK"
