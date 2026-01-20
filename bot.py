import os
import asyncio
import logging
from pyrogram import Client, filters
from quart import Quart, Response, request, stream_with_context

# Enable logging to see activity in Koyeb Console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
API_ID = int(os.environ.get("API_ID", 27479878))
API_HASH = os.environ.get("API_HASH", "05f8dc8265d4c5df6376dded1d71c0ff")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DOMAIN = os.environ.get("DOMAIN", "international-angelia-uhhy5-754bbc99.koyeb.app")
PORT = int(os.environ.get("PORT", 8080))

app = Quart(__name__)
# in_memory=True is essential for Koyeb's non-persistent storage
bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

@app.route('/')
async def health():
    return "OK", 200

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    logger.info(f"Start command received from {message.from_user.id}")
    await message.reply_text("👋 Bot is active! Send a video for a link.")

@bot.on_message((filters.video | filters.document) & filters.private)
async def handle_media(client, message):
    logger.info(f"Media received from {message.from_user.id}")
    stream_url = f"https://{DOMAIN}/stream/{message.id}?chat={message.chat.id}"
    await message.reply_text(f"🎥 **Stream Link:**\n`{stream_url}`")

@app.route('/stream/<int:message_id>')
async def stream_video(message_id):
    chat_id = request.args.get("chat")
    @stream_with_context
    async def generate():
        try:
            msg = await bot.get_messages(int(chat_id), message_id)
            async for chunk in bot.stream_media(msg):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming error: {e}")
    return Response(generate(), mimetype="video/mp4")

async def main():
    logger.info("Starting Bot...")
    await bot.start()
    logger.info("Bot started. Starting Web Server...")
    # Use idle() to keep the bot listening while Quart runs
    config = asyncio.create_task(app.run_task(host='0.0.0.0', port=PORT))
    await asyncio.Event().wait() # Keeps the script running

if __name__ == "__main__":
    asyncio.run(main())
