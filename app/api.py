"""
Optional API wrapper for the Wordle bot.
This allows the bot to be used as a web service.
"""
import time
from pydantic import BaseModel

from fastapi import FastAPI
from .main import run_wordle_bot

# Create FastAPI app
app = FastAPI(title="Wordle Bot API", description="AI-powered Wordle solver")

class RunPayload(BaseModel):
    """Payload for running the Wordle bot."""
    language: str
    model: str = "gpt-4o-mini"
    save_to_db: bool = True

@app.post("/run")
def run_bot_api(payload: RunPayload):
    """API endpoint to run the Wordle bot."""
    return run_wordle_bot(payload.language, payload.model, payload.save_to_db)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
