from fastapi import FastAPI
from langchain.llms import Ollama
from pydantic_settings import BaseSettings

app = FastAPI(title="User Story Assistant")

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "User Story Assistant API is running"
    }
