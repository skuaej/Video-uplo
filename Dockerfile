FROM python:3.10-slim

WORKDIR /app

# System dependencies (safe minimal)
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app.py .

# Koyeb provides PORT env var
ENV PORT=8080
EXPOSE 8080

# Run with gunicorn
CMD ["sh", "-c", "gunicorn -w 2 -b 0.0.0.0:${PORT} app:app"]
