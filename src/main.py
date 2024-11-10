from fastapi import FastAPI
from langchain_ollama import OllamaLLM as Ollama
from pydantic_settings import BaseSettings
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="User Story Assistant")

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "User Story Assistant API is running"
    }
