AI-Powered Turkish Wordle Solver

This project is a Python-based AI agent that autonomously plays and solves the Turkish version of Wordle found at wordleturkce.bundle.app.

It uses the Selenium library to control a web browser and interact with the game's interface, and leverages OpenAI's GPT models to make intelligent guesses based on the game's feedback.

<img src="img/bot.gif" width="480" height="600" />

Features

- Autonomous Gameplay: Launches a browser, navigates to the game, and plays without human intervention.

- AI-Driven Logic: Uses an OpenAI model (e.g., gpt-4o-mini) to analyze the game state and make strategic guesses.

- Intelligent Prompting: Compiles a detailed set of rules from the game history (green, yellow, and gray letters) to guide the AI's decisions.

- Error Handling: Can detect when a word is rejected by the game and when it repeats a guess, prompting the AI for a new one.

- Robust Automation: Implements patient waits and "wake-up" keystrokes to handle the dynamic nature of modern web applications.


Setup Instructions

Follow these steps to get the Wordle solver running on your local machine.
1. Prerequisites

    Python 3.8+: Make sure you have Python installed. You can download it from python.org.

    Mozilla Firefox: The script is configured to use Firefox. Please ensure it is installed.

2. Get the Code

    Download the wordle_bot.py script and place it in a new folder on your computer.

3. Install Dependencies

    Open a terminal or command prompt in the project folder.

    Install the necessary Python libraries:

    pip install selenium openai

4. Download the Web Driver

    This script uses geckodriver to control Firefox.

    Go to the geckodriver releases page.

    Download the correct version for your operating system (e.g., win64 for Windows, macos for Mac).

    Unzip the file and place the geckodriver executable in the same folder as your wordle_bot.py script.

5. Configure API Key

    Open the wordle_bot.py script in a text editor.

    Find the following line near the top:

    OPENAI_API_KEY = "YOUR_API_KEY_HERE"

    Replace "YOUR_API_KEY_HERE" with your actual OpenAI API key.

How to Run

Once you have completed the setup, you can run the agent from your terminal:

```
python wordle_bot.py
```

The script will launch a new Firefox window, navigate to the Wordle website, and begin solving the puzzle. You can watch its progress in both the browser window and the terminal output.
How It Works

1. Browser Control: The script uses Selenium to launch and control a Firefox browser. It navigates the website's complex nested structure (including Shadow DOMs) to find and click the virtual keyboard keys.

2. State Analysis: After each guess, the script reads the color of the tiles (Green, Yellow, Gray) to determine the result.

3. AI Prompting: This result is compiled into a detailed set of rules and constraints. This summary is sent to the OpenAI API.

4. Intelligent Guessing: The AI model receives the rules (e.g., "must use 'A'", "must not use 'B'", "don't repeat old guesses") and provides the next best strategic guess.

5. Loop: The script types the new guess, and the cycle repeats until the word is solved or it runs out of attempts.