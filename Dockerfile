# Force fresh build 2025-10-06
FROM python:3.11.9-slim
RUN apt-get update && apt-get install -y \
    libssl-dev \
    python3-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || { echo "pip install failed"; exit 1; }
RUN pip list
COPY . .
EXPOSE $PORT
CMD uvicorn main:app --host 0.0.0.0 --port $PORT --log-level debug
