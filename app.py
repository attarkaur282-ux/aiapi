from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from typing import Optional
import os

# ================================================================
# CONFIG
# ================================================================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-583e4a59c58e480384006e9b217f2087")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# ================================================================
# APP
# ================================================================
app = FastAPI(
    title="DeepSeek Reply API",
    description="Powered by @notxsatvir",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
# MODELS
# ================================================================
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "deepseek-chat"
    thinking: Optional[bool] = False
    reasoning_effort: Optional[str] = "high"
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = 4096
    system_prompt: Optional[str] = "You are a helpful assistant."

# ================================================================
# DEEPSEEK API CALL
# ================================================================
async def call_deepseek(request: ChatRequest):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    messages = [
        {"role": "system", "content": request.system_prompt},
        {"role": "user", "content": request.message}
    ]
    
    payload = {
        "model": request.model,
        "messages": messages,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "stream": False
    }
    
    if request.thinking:
        payload["thinking"] = {"type": "enabled"}
        payload["reasoning_effort"] = request.reasoning_effort
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"DeepSeek API Error: {response.text}"
            )
        
        return response.json()

# ================================================================
# API ENDPOINTS
# ================================================================

@app.get("/")
async def root():
    return {
        "name": "DeepSeek Reply API",
        "developer": "@notxsatvir",
        "version": "1.0",
        "status": "active ✅",
        "endpoints": {
            "/": "API Info",
            "/models": "Available models",
            "/chat?message=Hello": "Chat with DeepSeek (GET)",
            "/chat": "Chat with DeepSeek (POST)"
        }
    }

@app.get("/models")
async def get_models():
    return {
        "models": [
            {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "Default"},
            {"id": "deepseek-coder", "name": "DeepSeek Coder", "description": "Best for coding"},
            {"id": "deepseek-reasoner", "name": "DeepSeek Reasoner", "description": "With reasoning"}
        ]
    }

@app.get("/chat")
async def chat_get(
    message: str = Query(..., description="Your message"),
    model: str = Query("deepseek-chat", description="Model name"),
    thinking: bool = Query(False, description="Enable thinking mode"),
    system: str = Query("You are a helpful assistant.", description="System prompt")
):
    """Chat with DeepSeek AI (GET - Browser friendly)"""
    
    if not DEEPSEEK_API_KEY:
        return {
            "success": False,
            "error": "❌ API Key not configured!",
            "developer": "@notxsatvir"
        }
    
    request = ChatRequest(
        message=message,
        model=model,
        thinking=thinking,
        system_prompt=system
    )
    
    try:
        result = await call_deepseek(request)
        
        reply = result["choices"][0]["message"]["content"]
        thinking_content = result["choices"][0]["message"].get("reasoning_content", None)
        usage = result.get("usage", {})
        model_used = result.get("model", model)
        
        return {
            "success": True,
            "reply": reply,
            "thinking_content": thinking_content,
            "model": model_used,
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            },
            "developer": "@notxsatvir"
        }
        
    except HTTPException as e:
        return {
            "success": False,
            "error": f"❌ {e.detail}",
            "developer": "@notxsatvir"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"❌ Error: {str(e)}",
            "developer": "@notxsatvir"
        }

@app.post("/chat")
async def chat_post(request: ChatRequest):
    """Chat with DeepSeek AI (POST)"""
    return await chat_get(
        message=request.message,
        model=request.model,
        thinking=request.thinking,
        system=request.system_prompt
    )
