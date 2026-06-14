FROM python:3.10-slim

WORKDIR /app

# Install dependencies first (takes advantage of Docker caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Match the port in your bot.py
ENV PORT=8000
EXPOSE 8000

# Run the bot
CMD ["python", "bot.py"]
