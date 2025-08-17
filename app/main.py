"""
Main entry point for the Wordle bot.
This provides both CLI interface and programmatic access.
"""
import time
import argparse
import sys
import os

# Add the parent directory to sys.path for imports when run directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try relative imports first (when imported as module)
    from .navigator.tr_navigator import TrNavigator
    from .navigator.en_navigator import EnNavigator
    from .agents.tr_agent import TrAgent
    from .agents.en_agent import EnAgent
    from .db import Database
    from .run import run_game
except ImportError:
    # Fall back to absolute imports (when run directly)
    from app.navigator.tr_navigator import TrNavigator
    from app.navigator.en_navigator import EnNavigator
    from app.agents.tr_agent import TrAgent
    from app.agents.en_agent import EnAgent
    from app.db import Database
    from app.run import run_game

def run_wordle_bot(language: str, model: str = "gpt-4o-mini", save_to_db: bool = True):
    """Main function to run the Wordle bot."""
    if language == "en":
        url = "https://www.nytimes.com/games/wordle/index.html"
        navigator = EnNavigator(url=url)
        agent = EnAgent(model=model)
    elif language == "tr":
        url = "https://wordleturkce.bundle.app/"
        navigator = TrNavigator(url=url)
        agent = TrAgent(model=model)
    else:
        raise ValueError(f"Unsupported language: {language}")

    try:
        result = run_game(navigator, agent)

        if save_to_db:
            db = Database()
            db.save_result(
                run_date=time.strftime("%Y-%m-%d"),
                language=language,
                model=model,
                won=result["won"],
                history=result["history"],
                shareable_output=result["result"]
            )

        return result
    except Exception as e:
        print(f"Error running bot: {e}")
        return {"error": str(e)}

def main():
    """CLI entry point for the Wordle bot."""
    parser = argparse.ArgumentParser(description="Run the AI Wordle Bot")
    parser.add_argument("language", choices=["en", "tr"], help="Language to play (en/tr)")
    parser.add_argument("--model", default="gpt-4o-mini", help="AI model to use")
    parser.add_argument("--no-db", action="store_true", help="Don't save results to database")

    args = parser.parse_args()
    run_wordle_bot(args.language, args.model, save_to_db=not args.no_db)

if __name__ == "__main__":
    main()
