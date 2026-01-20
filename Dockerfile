FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 🔥 IMPORTANT FIX: run uvicorn instead of python app.py
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
