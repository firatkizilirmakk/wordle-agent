from .base import BaseAgent

class EnAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__()
        self.model = model
        self.system_prompt = """
        You are an expert English Wordle solver. You will be given the game state and a list of rules. Your goal is to provide the single best 5-letter English word as a guess.

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

    @property
    def simple_word(self):
        """Returns a simple word for the agent."""
        return "ARISE"

    def _get_user_prompt(self, history):
        """Generates the user prompt for the AI based on the game history."""
        previous_guesses = [turn["guess"] for turn in history]
        state = self.get_historic_state(history)
        green_letters, gray_letters, final_yellows = state["green_letters"], state["gray_letters"], state["yellow_letters"]

        user_prompt = "Here is the current game state. Follow the example and provide the next best guess.\n\n"
        user_prompt += "--- CURRENT GAME STATE ---\n"

        if not history:
            user_prompt += "This is the first guess\n"
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
        return user_prompt

    def get_ai_guess(self, history: list) -> str:
        """Generates a guess using the AI client based on the history of attempts."""
        user_prompt = self._get_user_prompt(history)

        messages = [{"role": "system", "content": self.system_prompt}, {"role": "user", "content": user_prompt}]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=4
            )

            ai_word = response.choices[0].message.content.strip().upper().replace(" ", "")
            ai_word_sanitized = "".join([c for c in ai_word if c.isalpha()]).upper()
            if len(ai_word_sanitized) > 5:
                ai_word_sanitized = ai_word_sanitized[:5]

            print(f"AI suggested: {ai_word_sanitized}")
            return ai_word_sanitized
        except Exception as e:
            print(f"An error occurred with the OpenAI API: {e}")
            return self.simple_word  # Fallback to a simple word if the API fails
