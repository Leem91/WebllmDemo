WebLLM Demo — Decision Intelligence Platform

This repository is a demo platform integrating a browser-side lightweight WebLLM (SmolLM2-360M) and an optional local backend Llama server (Llama-3.2-1B quantized via llama-cpp-python).

Structure:
- frontend/: Vite + Web UI (AI Copilot page, Live Feed, Member Ops)
- backend/: FastAPI backend, simulation engine, and local llama server wrapper

Quick start:
1. Backend: see backend/README_llama.md for Llama server instructions.
2. Frontend: cd frontend && npm install && npm run dev

Security and Notes:
- The local Llama server requires manual placement of quantized model files (due to licensing/size).
- /api/llm supports optional API key via X-LLM-API-KEY and basic in-memory rate limiting.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
