import time
from typing import Union
from pydantic import BaseModel

from .navigator.tr_navigator import TrNavigator
from .navigator.en_navigator import EnNavigator

from .agents.tr_agent import TrAgent
from .agents.en_agent import EnAgent

from .db import Database

from fastapi import FastAPI

# Create FastAPI app
app = FastAPI()
db = Database()

def run(navigator: Union[EnNavigator, TrNavigator], agent: Union[EnAgent, TrAgent]):
    """Runs the Wordle bot for the specified language."""
    history = []
    won = False
    for i in range(6): 
        current_attempt = i
        invalid_counter = 0
        use_simple_word = False
        while True:
            print("\nTurn {}".format(current_attempt + 1))
            if use_simple_word:
                guess = agent.simple_word
                use_simple_word = False
            else:
                guess = agent.get_ai_guess(history)
            if len(guess) != 5:
                history.append({"guess": guess, "feedback": "INVALID"})
                continue

            navigator.type_word(guess)
            time.sleep(5) 

            feedback = navigator.read_result(current_attempt)
            if feedback == "INVALID":
                print(f"Invalid word: {guess}. Invalid attempts: {invalid_counter + 1}")
                history.append({"guess": guess, "feedback": "INVALID"})
                navigator.clear_word(len(guess))

                invalid_counter += 1
                if invalid_counter > 5:
                    use_simple_word = True
                    invalid_counter = 0
                    print(f"Invalid attempts exceeded. Using simple word: {agent.simple_word}")
            else:
                history.append({"guess": guess, "feedback":feedback})
                break

        if feedback == "GGGGG":
            won = True
            break

    if won:
        print(f"SUCCESS! The word was '{guess}'. Solved in {current_attempt + 1} attempts.")
    else:
        print("FAILED! Could not solve in 6 attempts.")

    shareable_output = navigator.read_final_result(history)
    navigator.close_browser()
    return {
        "won": won,
        "attempts": current_attempt + 1,
        "history": history,
        "result": shareable_output,
        "final_word": guess if won else None
    }

class RunPayload(BaseModel):
    """Payload for running the Wordle bot."""
    language: str
    model: str = "gpt-4o-mini"

@app.post("/run_wordle_bot")
def run_wordle_bot(payload: RunPayload):
    """Runs the Wordle bot for the specified language."""
    if payload.language == "en":
        url = "https://www.nytimes.com/games/wordle/index.html"
        navigator = EnNavigator(url=url)
        agent = EnAgent(model=payload.model)
    elif payload.language == "tr":
        url = "https://wordleturkce.bundle.app/"
        navigator = TrNavigator(url=url)
        agent = TrAgent(model=payload.model)

    try:
        result = run(navigator, agent)
        db.save_result(
            run_date=time.strftime("%Y-%m-%d"),
            language=payload.language,
            model=payload.model,
            won=result["won"],
            history=result["history"]
        )
        return result
    except Exception as e:
        return {"error": str(e)}