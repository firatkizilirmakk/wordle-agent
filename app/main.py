import argparse
from run import run_wordle_bot

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
    run_wordle_bot(args.language)
