from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "c5dc372566601ed8745c469469e054e4")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

@app.get("/")
async def root():
    return JSONResponse({
        "status": "✅ API is live",
        "developer": "@notxsatvir",
        "message": "Use /chat?message=your+question"
    })

@app.get("/chat")
async def chat_get(message: str = Query(..., description="Your question")):
    try:
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
            response = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                return JSONResponse({
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "developer": "@notxsatvir"
                })
            
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            
            return JSONResponse({
                "success": True,
                "reply": reply,
                "developer": "@notxsatvir"
            })
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
            "developer": "@notxsatvir"
        })

@app.get("/test")
async def test():
    return JSONResponse({
        "message": "API is working!",
        "developer": "@notxsatvir"
    })
