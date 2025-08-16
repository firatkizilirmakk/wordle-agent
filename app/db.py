import sqlite3
import json
from datetime import datetime
import pandas as pd

class Database:
    """A class to manage the SQLite database for Wordle results."""

    def __init__(self, db_name="wordle.db"):
        """
        Initializes the Database class and creates the database/table if they don't exist.

        Args:
            db_name (str): The name of the SQLite database file.
        """
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        """Initializes the database connection and creates the results table."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    run_date TEXT NOT NULL,
                    language TEXT NOT NULL,
                    model TEXT NOT NULL,
                    won BOOLEAN NOT NULL,
                    history TEXT,
                    timestamp DATETIME NOT NULL,
                    PRIMARY KEY (run_date, language, model)
                )
            ''')
            conn.commit()
        print("Database initialized successfully.")

    def save_result(self, run_date: str, language: str, model: str, won: bool, history: list):
        """
        Saves a single game result to the database.

        Args:
            run_date (str): The date of the game run.
            language (str): The language of the game ('en' or 'tr').
            won (bool): Whether the game was won.
            history (list): A list of dictionaries representing the game history.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            history_json = json.dumps(history)
            
            cursor.execute('''
                INSERT INTO results (run_date, language, model, won, history, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (run_date, language, model, won, history_json, datetime.now()))

            conn.commit()
        print(f"Result for {language.upper()} Wordle saved to database.")

    def get_all_results(self):
        """Fetches all game results from the database."""
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql_query("SELECT * FROM results", conn)
        return df
