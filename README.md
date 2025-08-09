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
- **Error Handling**: Detects invalid words, repeated guesses, and prompts AI for new attempts with fallback to simple words
- **Robust Automation**: Implements patient waits and handles dynamic web application behavior including Shadow DOM
- **Modular Architecture**: Clean separation between navigation logic and AI agents
- **FastAPI Integration**: Includes REST API endpoints for programmatic access
- **Advanced DOM Handling**: Sophisticated navigation through complex web structures including Shadow DOM elements

## Project Structure

```
wordle-agent/
├── app/                          # Main application package
│   ├── main.py                  # CLI entry point with argument parsing
│   ├── run.py                   # Core game logic and FastAPI application
│   ├── agents/                  # AI agents for different languages
│   │   ├── base.py             # Base agent with OpenAI integration and state management
│   │   ├── en_agent.py         # English Wordle AI agent with specialized prompting
│   │   └── tr_agent.py         # Turkish Wordle AI agent with Turkish character support
│   └── navigator/              # Browser automation modules
│       ├── base.py             # Base navigator with Firefox/Selenium setup
│       ├── en_navigator.py     # NYT Wordle navigation with complex DOM handling
│       └── tr_navigator.py     # Turkish Wordle navigation with Shadow DOM support
├── .env                        # Environment variables (OpenAI API key)
└── README.md                   # This file
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
pip install selenium openai python-dotenv fastapi uvicorn
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

### Using the Main Application

The main application provides a clean CLI interface to run either language variant:

```bash
# Run Turkish Wordle solver
python app/main.py --language tr

# Run English Wordle solver  
python app/main.py --language en

# Default is English if no language specified
python app/main.py
```

### Using the FastAPI Application

You can also run the application as a web service:

```bash
# Start the FastAPI server (from the app directory)
cd app
python -c "import uvicorn; from run import app; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

Then make POST requests to:
- `http://localhost:8000/run_wordle_bot/en` for English Wordle
- `http://localhost:8000/run_wordle_bot/tr` for Turkish Wordle

The API returns JSON with game results including win status, number of attempts, game history, and shareable output.

**Note**: The script will:
1. Launch a new Firefox window
2. Navigate to the appropriate Wordle website
3. Begin solving the puzzle autonomously
4. Display progress in both the browser window and terminal output
5. Return detailed results including game history and shareable format

## How It Works

### Architecture Overview

The bot uses a modular architecture with separate components for navigation and AI logic:

1. **Navigators** (`navigator/`): Handle browser automation and game interaction
   - `BaseNavigator`: Common Selenium setup and driver management with Firefox
   - `EnNavigator`: NYT Wordle-specific navigation (complex DOM and CSS selector handling)
   - `TrNavigator`: Turkish Wordle-specific navigation (Shadow DOM traversal)

2. **Agents** (`agents/`): Handle AI logic and decision making
   - `BaseAgent`: OpenAI client setup and comprehensive game state analysis
   - `EnAgent`: English word strategy with optimized prompting for GPT-4o-mini
   - `TrAgent`: Turkish word strategy with Turkish character support and specialized prompting

3. **Core Logic** (`run.py`): Game orchestration and FastAPI integration
   - Main game loop with intelligent retry mechanisms
   - Invalid word detection and fallback strategies
   - Shareable result generation
   - REST API endpoints for programmatic access

### Game Flow

1. **Browser Control**: Uses Selenium with Firefox to launch and control the browser, navigating complex DOM structures including Shadow DOMs for modern web applications

2. **State Analysis**: After each guess, reads tile colors (Green, Yellow, Gray) to determine feedback:
   - **Green (G)**: Correct letter in correct position
   - **Yellow (Y)**: Correct letter in wrong position  
   - **Gray (B)**: Letter not in the word

3. **AI Prompting**: Compiles comprehensive game history into detailed constraints and rules, then sends to OpenAI's gpt-4o-mini model with language-specific prompts

4. **Intelligent Guessing**: AI model receives structured rules (e.g., "must use 'A' in position 2", "must not use 'B'", "don't repeat previous guesses") and provides the next strategic guess

5. **Error Handling**: 
   - Detects invalid words and repeated guesses
   - Implements retry logic with fallback to simple known words
   - Handles timeout and DOM loading issues gracefully

6. **Loop**: Types the new guess and repeats until the word is solved or 6 attempts are exhausted

### Advanced Features

- **Shadow DOM Navigation**: Sophisticated traversal of nested Shadow DOM elements in modern web applications
- **Dynamic Wait Strategies**: Patient waiting for animations and DOM updates to complete
- **Clipboard Integration**: Automatic extraction of shareable game results
- **Character Encoding**: Proper handling of Turkish characters (Ö, Ü, Ğ, Ş, İ, Ç)
- **Fallback Mechanisms**: Multiple layers of error recovery and retry logic

### Language-Specific Features

- **Turkish**: 
  - Uses Turkish character set and word patterns
  - Includes comprehensive Turkish word list (2800+ words)
  - Handles Turkish character encoding (ÖÜĞŞİÇ → öüğşiç)
  - Specialized prompting for Turkish grammar and word formation
  - Shadow DOM navigation for wordleturkce.bundle.app

- **English**: 
  - Optimized for NYT Wordle interface and English word patterns
  - Complex CSS selector-based navigation
  - Fallback word: "ARISE" (high vowel frequency)
  - Temperature-controlled AI responses (0.3) for balanced creativity

- **Extensible**: Easy to add new languages by creating new agent/navigator pairs following the established patterns

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Customization Options

- **Model Selection**: Both agents use gpt-4o-mini with different temperature settings
- **Headless Mode**: Commented out in navigator classes - uncomment for background execution
- **Timeout Settings**: Adjustable wait times in navigator classes for slower connections
- **Simple Words**: Customizable fallback words for each language in agent classes
- **API Parameters**: Configurable max_tokens (currently 4) and temperature settings

### API Response Format

The FastAPI endpoints return structured JSON responses:

```json
{
  "won": true,
  "attempts": 4,
  "history": [
    {"guess": "ARISE", "feedback": "YBBGB"},
    {"guess": "ROAST", "feedback": "GGGGG"}
  ],
  "result": "🟨⬜⬜🟩⬜\n🟩🟩🟩🟩🟩"
}
```

## Troubleshooting

### Common Issues

1. **Firefox/Geckodriver Issues**:
   - Ensure Firefox is installed and updated to the latest version
   - Download the correct geckodriver version for your OS and architecture
   - Make geckodriver executable on Linux/Mac: `chmod +x geckodriver`
   - Verify geckodriver is in the project root directory

2. **OpenAI API Issues**:
   - Verify your OpenAI API key is correct and has sufficient credits
   - Check that the `.env` file is in the project root directory
   - Ensure the API key has access to gpt-4o-mini model
   - Monitor API usage to avoid rate limits

3. **Web Scraping Issues**:
   - Websites may change their structure; DOM selectors might need updates
   - Some sites may have anti-bot measures; running in non-headless mode may help
   - Shadow DOM elements may load asynchronously; increase timeout if needed
   - Clear browser cache if experiencing persistent issues

4. **Dependencies**:
   - Ensure all required packages are installed: `pip install selenium openai python-dotenv fastapi uvicorn`
   - Check that your Python version is 3.8 or higher
   - Verify tkinter is available for clipboard operations

5. **Game-Specific Issues**:
   - Turkish characters may not display correctly - ensure proper encoding
   - Invalid word detection may fail if the game interface changes
   - Timeout issues may occur with slow internet connections

### Debug Tips

- Run in non-headless mode to observe browser behavior
- Check browser console for JavaScript errors
- Monitor network requests for API failures
- Use verbose logging in navigator classes for detailed debugging

## Performance Notes

- **Average solve time**: 3-5 attempts for most words
- **Success rate**: ~95% for valid dictionary words
- **AI response time**: 1-3 seconds per guess
- **Total game time**: 2-4 minutes including browser automation

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the existing code style
4. Add tests if applicable
5. Update documentation as needed
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Submit a pull request

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add docstrings to new methods and classes
- Test with both English and Turkish variants
- Ensure backward compatibility with existing API
- Document any new configuration options

### Areas for Improvement

- Support for additional Wordle variants and languages
- Enhanced AI strategies and word selection algorithms
- Performance optimizations for faster gameplay
- Better error handling and recovery mechanisms
- Comprehensive test suite with automated testing

## License

This project is for educational and research purposes. Please respect the terms of service of the Wordle websites when using this bot. The code is provided as-is without warranty.
