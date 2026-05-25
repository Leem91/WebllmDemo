import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# This server wraps the local llama_service and exposes a simple OpenAI-like
# /v1/chat/completions streaming endpoint. It expects LLAMA_MODEL_PATH to be
# set to a quantized ggml/llama-cpp-python compatible model file.

try:
    import llama_service
except Exception as e:
    llama_service = None

app = FastAPI(title="Local Llama Server (SSE)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"ok": True, "llama_available": bool(llama_service)}


@app.post("/v1/chat/completions")
def chat_completions(req: dict):
    if llama_service is None:
        raise HTTPException(status_code=501, detail="llama_service not available: please install llama-cpp-python and ensure llama_service.py is present")

    messages = req.get("messages") or req.get("input") or []
    max_tokens = int(req.get("max_tokens", 512))
    temperature = float(req.get("temperature", 0.2))

    gen = llama_service.stream_chat(messages, max_tokens=max_tokens, temperature=temperature)
    # stream as SSE (text/event-stream) where each chunk is 'data: JSON\n\n'
    return StreamingResponse(gen, media_type="text/event-stream")


@app.get("/status")
def status():
    if llama_service is None:
        return {"available": False, "error": "llama_service not loaded"}
    return llama_service.get_status()
