Local Llama Server (instructions)

Overview:
- This repository includes a lightweight local Llama server wrapper (backend/llama_server.py) that uses llama_service.py to stream responses via Server-Sent Events (SSE).

Prerequisites:
- Python 3.10+ and pip
- A quantized Llama-compatible model file (ggml/llama-cpp-python compatible). Place it at backend/models/<model-file> or set LLAMA_MODEL_PATH env var.

Quick start (venv recommended):
1. cd backend
2. python -m venv .venv && source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
3. pip install -r requirements.txt
4. export LLAMA_MODEL_PATH=./models/your-quantized-model.bin
5. python -m uvicorn llama_server:app --host 0.0.0.0 --port 8080

Docker (example):
1. docker build -t qcode-llama:latest .
2. docker run --rm -p 8080:8080 -e LLAMA_MODEL_PATH=/app/models/your-model.bin qcode-llama:latest

Notes:
- Building llama-cpp-python may require additional system libraries depending on platform.
- This setup intentionally does NOT auto-download model weights. Download/placement of model files must be performed by the user to respect licensing and storage constraints.
