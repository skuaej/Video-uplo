import os
import asyncio
import logging
import threading
from pyrogram import Client, filters, idle
from flask import Flask

# 1. Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Config
API_ID = int(os.environ.get("API_ID", 27479878))
API_HASH = os.environ.get("API_HASH", "05f8dc8265d4c5df6376dded1d71c0ff")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DOMAIN = os.environ.get("DOMAIN", "international-angelia-uhhy5-754bbc99.koyeb.app")

# 3. The Web Server (Flask is lighter for health checks)
web_app = Flask(__name__)

@web_app.route('/')
def health():
    return "ALIVE", 200

def run_web():
    port = int(os.environ.get("PORT", 8000))
    web_app.run(host='0.0.0.0', port=port)

# 4. The Bot
bot = Client("stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    logger.info("RECEIVED START COMMAND")
    await message.reply_text("🚀 **SYSTEM ONLINE.** Send a video.")

@bot.on_message((filters.video | filters.document) & filters.private)
async def handle_video(client, message):
    link = f"https://{DOMAIN}/stream/{message.id}?chat={message.chat.id}"
    await message.reply_text(f"🎥 **Link:** `{link}`")

# 5. The Launch Sequence
if __name__ == "__main__":
    # Start Web Server in a background thread
    threading.Thread(target=run_web, daemon=True).start()
    logger.info("Web Server Thread Started.")

    # Start Bot in the main thread
    bot.run()
