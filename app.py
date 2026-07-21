from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-583e4a59c58e480384006e9b217f2087")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

@app.get("/")
def root():
    return {
        "status": "✅ API is live",
        "developer": "@notxsatvir"
    }

@app.get("/chat")
async def chat_get(message: str = Query(...)):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": message}],
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{DEEPSEEK_BASE_URL}/chat/completions", headers=headers, json=payload)
        data = resp.json()
        return {
            "reply": data["choices"][0]["message"]["content"],
            "developer": "@notxsatvir"
        }
