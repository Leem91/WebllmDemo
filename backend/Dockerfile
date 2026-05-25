FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps often required to build/compile llama-cpp-python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git libopenblas-dev libomp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "llama_server:app", "--host", "0.0.0.0", "--port", "8080"]
