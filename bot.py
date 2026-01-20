import os
import asyncio
import logging
from pyrogram import Client, filters
from quart import Quart, Response, request, stream_with_context

# 1. Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Config
API_ID = int(os.environ.get("API_ID", 27479878))
API_HASH = os.environ.get("API_HASH", "05f8dc8265d4c5df6376dded1d71c0ff")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DOMAIN = os.environ.get("DOMAIN", "international-angelia-uhhy5-754bbc99.koyeb.app")
PORT = int(os.environ.get("PORT", 8000))

app = Quart(__name__)
bot = Client("stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# --- WEB ROUTES ---

@app.route('/')
async def health():
    return "Bot is Online!", 200

@app.route('/stream/<int:message_id>')
async def stream_video(message_id):
    chat_id = request.args.get("chat")
    if not chat_id:
        return "Error: Missing Chat ID", 400

    @stream_with_context
    async def generate():
        try:
            # We fetch the message inside the stream to ensure the bot is ready
            msg = await bot.get_messages(int(chat_id), message_id)
            async for chunk in bot.stream_media(msg):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming error: {e}")

    return Response(generate(), mimetype="video/mp4")

# --- BOT HANDLERS ---

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("🚀 **System Online!**\nSend a video to get a 3GB+ stream link.")

@bot.on_message((filters.video | filters.document) & filters.private)
async def handle_video(client, message):
    # This generates the link you were trying to visit
    link = f"https://{DOMAIN}/stream/{message.id}?chat={message.chat.id}"
    await message.reply_text(f"🎥 **Stream Link:**\n`{link}`")

# --- EXECUTION ---

async def main():
    # Start the bot
    await bot.start()
    logger.info("Bot started.")
    
    # Start the web server as a background task
    # This keeps the '/' and '/stream' routes active
    loop = asyncio.get_event_loop()
    loop.create_task(app.run_task(host='0.0.0.0', port=PORT))
    
    # Keep the process alive
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
