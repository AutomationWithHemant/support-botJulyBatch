"""
app.py - FastAPI server for the bot.
Start:   uvicorn app:app --port 8000
Swagger: http://localhost:8000/docs
Chat UI: http://localhost:8000/        (used by the Playwright UI tests)
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from rag_bot import ask

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="QodeBench Support Bot")


class Question(BaseModel):
    question: str


@app.post("/chat")
def chat(payload: Question):
    return {"answer": ask(payload.question)}


@app.get("/health")
def health():
    # quick "is the server up?" check - used by run_all.py before UI/API tests
    return {"status": "ok"}


@app.get("/")
def chat_page():
    return FileResponse(BASE_DIR / "chat.html")
