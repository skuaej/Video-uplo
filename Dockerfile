FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start app
CMD ["python", "app.py"]
