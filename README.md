# AI-Powered Wordle Solver

This project is a Python-based AI agent that autonomously plays and solves Wordle in both **Turkish** and **English**. It supports:
- Turkish Wordle at [wordleturkce.bundle.app](https://wordleturkce.bundle.app/)
- English Wordle at [The New York Times](https://www.nytimes.com/games/wordle/index.html)

The bot uses Selenium to control a web browser and interact with the game's interface, leveraging OpenAI's GPT models to make intelligent guesses based on game feedback.


## Features

- **Multi-Language Support**: Play both Turkish and English Wordle variants
- **Autonomous Gameplay**: Launches a browser, navigates to the game, and plays without human intervention
- **AI-Driven Logic**: Uses OpenAI models (e.g., gpt-4o-mini) to analyze game state and make strategic guesses
- **Intelligent Prompting**: Compiles detailed rules from game history (green, yellow, and gray letters) to guide AI decisions
- **Error Handling**: Detects invalid words, repeated guesses, and prompts AI for new attempts
- **Robust Automation**: Implements patient waits and handles dynamic web application behavior
- **Modular Architecture**: Clean separation between navigation logic and AI agents

## Package Structure

```
wordlebot/
├── app/                           # Main application package
│   ├── main.py                   # Entry point with CLI interface
│   ├── agents/                   # AI agents for different languages
│   │   ├── base.py               # Base agent with OpenAI integration
│   │   ├── en_agent.py           # English Wordle AI agent
│   │   └── tr_agent.py           # Turkish Wordle AI agent
│   └── navigator/                # Browser automation modules
│       ├── base.py               # Base navigator with Selenium setup
│       ├── en_navigator.py       # NYT Wordle navigation logic
│       └── tr_navigator.py       # Turkish Wordle navigation logic
├── en.py                         # Standalone English Wordle solver
├── tr.py                         # Standalone Turkish Wordle solver
├── turkish_words.txt             # Turkish word list
├── geckodriver                   # Firefox WebDriver executable
├── .env                          # Environment variables (API keys)
└── README.md                     # This file
```

## Setup Instructions

Follow these steps to get the Wordle solver running on your local machine.

### 1. Prerequisites

- **Python 3.8+**: Make sure you have Python installed. You can download it from [python.org](https://python.org).
- **Mozilla Firefox**: The script is configured to use Firefox. Please ensure it is installed.

### 2. Clone the Repository

```bash
git clone https://github.com/firatkizilirmakk/wordle-agent.git
cd wordle-agent
```

### 3. Install Dependencies

Install the necessary Python libraries:

```bash
pip install selenium openai python-dotenv
```

### 4. Download the Web Driver

This script uses `geckodriver` to control Firefox.

- Go to the [geckodriver releases page](https://github.com/mozilla/geckodriver/releases)
- Download the correct version for your operating system (e.g., `linux64`, `win64`, `macos`)
- Extract the executable and place it in the project root directory as `geckodriver`
- Make sure it's executable on Linux/Mac: `chmod +x geckodriver`

### 5. Configure API Key

Create a `.env` file in the project root and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_actual_api_key_here
```

You can get an API key from [OpenAI's platform](https://platform.openai.com/api-keys).

## How to Run

### Using the Main Application (Recommended)

The main application provides a clean CLI interface to run either language variant:

```bash
# Run Turkish Wordle solver
python app/main.py --language tr

# Run English Wordle solver  
python app/main.py --language en

# Default is English if no language specified
python app/main.py
```

### Using Standalone Scripts

You can also run the standalone scripts directly:

```bash
# Turkish Wordle
python tr.py

# English Wordle
python en.py
```

**Note**: The standalone scripts may require manual API key configuration within the files.

The script will:
1. Launch a new Firefox window
2. Navigate to the appropriate Wordle website
3. Begin solving the puzzle autonomously
4. Display progress in both the browser window and terminal output

## How It Works

## How It Works

### Architecture Overview

The bot uses a modular architecture with separate components for navigation and AI logic:

1. **Navigators** (`navigator/`): Handle browser automation and game interaction
   - `BaseNavigator`: Common Selenium setup and driver management
   - `EnNavigator`: NYT Wordle-specific navigation (Shadow DOM handling)
   - `TrNavigator`: Turkish Wordle-specific navigation

2. **Agents** (`agents/`): Handle AI logic and decision making
   - `BaseAgent`: OpenAI client setup and game state analysis
   - `EnAgent`: English word strategy and prompting
   - `TrAgent`: Turkish word strategy and prompting

### Game Flow

1. **Browser Control**: Uses Selenium to launch and control Firefox, navigating complex DOM structures including Shadow DOMs for modern web applications

2. **State Analysis**: After each guess, reads tile colors (Green, Yellow, Gray) to determine feedback:
   - **Green**: Correct letter in correct position
   - **Yellow**: Correct letter in wrong position  
   - **Gray**: Letter not in the word

3. **AI Prompting**: Compiles game history into detailed constraints and rules, then sends to OpenAI API with language-specific prompts

4. **Intelligent Guessing**: AI model receives rules (e.g., "must use 'A' in position 2", "must not use 'B'", "don't repeat previous guesses") and provides the next strategic guess

5. **Error Handling**: Detects invalid words, repeated guesses, and other game errors, prompting AI for alternatives

6. **Loop**: Types the new guess and repeats until the word is solved or 6 attempts are exhausted

### Language-Specific Features

### Language-Specific Features

- **Turkish**: Uses Turkish character set and word patterns, includes Turkish word list
- **English**: Optimized for NYT Wordle interface and English word patterns
- **Extensible**: Easy to add new languages by creating new agent/navigator pairs

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Customization

- **Model Selection**: Modify the agent classes to use different OpenAI models (e.g., gpt-4, gpt-3.5-turbo)
- **Headless Mode**: Uncomment the headless option in navigator classes for background execution
- **Timeout Settings**: Adjust wait times in navigator classes for slower connections

## Troubleshooting

### Common Issues

1. **Firefox/Geckodriver Issues**:
   - Ensure Firefox is installed and updated
   - Download the correct geckodriver version for your OS
   - Make geckodriver executable on Linux/Mac: `chmod +x geckodriver`

2. **API Key Issues**:
   - Verify your OpenAI API key is correct and has sufficient credits
   - Check that the `.env` file is in the project root directory

3. **Web Scraping Issues**:
   - Websites may change their structure; DOM selectors might need updates
   - Some sites may have anti-bot measures; running in non-headless mode may help

4. **Dependencies**:
   - Ensure all required packages are installed: `pip install selenium openai python-dotenv`
   - Check that your Python version is 3.8 or higher

## Contributing

Feel free to submit issues and enhancement requests! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Please respect the terms of service of the Wordle websites when using this bot.