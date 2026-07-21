from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Optional
import os

# ================================================================
# CONFIG
# ================================================================
DEEPSEEK_API_KEY = "sk-583e4a59c58e480384006e9b217f2087"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# ================================================================
# APP
# ================================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
# API ENDPOINTS
# ================================================================

@app.get("/")
async def root():
    return {
        "name": "DeepSeek Reply API",
        "developer": "@notxsatvir",
        "version": "1.0",
        "status": "active",
        "message": "✅ API is working! Use /chat?message=your_message"
    }

@app.get("/chat")
async def chat(
    message: str = Query(..., description="Your message"),
    model: str = Query("deepseek-v4-pro", description="Model name"),
    thinking: bool = Query(True, description="Enable thinking mode"),
    system: str = Query("You are a helpful assistant.", description="System prompt")
):
    """Chat with DeepSeek AI"""
    
    if not DEEPSEEK_API_KEY:
        return {
            "success": False,
            "error": "❌ API Key not configured!",
            "developer": "@notxsatvir"
        }
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": message}
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 1.0,
            "max_tokens": 4096,
            "stream": False,
            "thinking": {"type": "enabled"} if thinking else {"type": "disabled"},
            "reasoning_effort": "high"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"DeepSeek API Error: {response.status_code}",
                    "detail": response.text[:200],
                    "developer": "@notxsatvir"
                }
            
            result = response.json()
            
            reply = result["choices"][0]["message"]["content"]
            thinking_content = result["choices"][0]["message"].get("reasoning_content", None)
            usage = result.get("usage", {})
            
            return {
                "success": True,
                "reply": reply,
                "thinking_content": thinking_content,
                "model": model,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                "developer": "@notxsatvir"
            }
        
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "❌ Request timeout! Try again.",
            "developer": "@notxsatvir"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"❌ Error: {str(e)}",
            "developer": "@notxsatvir"
        }

# ================================================================
# FOR VERCEL - IMPORTANT FIX
# ================================================================
handler = app
