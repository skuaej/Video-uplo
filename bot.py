import os
import asyncio
import logging
from pyrogram import Client, filters, idle
from quart import Quart, Response, request, stream_with_context

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Config ---
API_ID = int(os.environ.get("API_ID", 27479878))
API_HASH = os.environ.get("API_HASH", "05f8dc8265d4c5df6376dded1d71c0ff")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8899757045:AAE19C08QRGCQWfynDhqUmXUzz0CDFDNE5g")
SESSION_STRING = os.environ.get("SESSION_STRING", None)
# .rstrip("/") ensures we don't accidentally create double slashes in the URL
DOMAIN = os.environ.get("DOMAIN", "https://estimated-koala-uhhy5-14868343.koyeb.app").rstrip("/")
PORT = int(os.environ.get("PORT", 8000))

app = Quart(__name__)

# --- Bot Initialization ---
if SESSION_STRING:
    bot = Client("stream_bot", session_string=SESSION_STRING, in_memory=True)
else:
    bot = Client("stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# --- Quart Routes ---
@app.route('/')
async def health():
    return "Bot is Streaming!", 200

@app.route('/stream/<int:message_id>')
async def stream_video(message_id):
    chat_id = request.args.get("chat")
    
    if not chat_id:
        return "Missing chat ID", 400

    @stream_with_context
    async def generate():
        try:
            # Fetch the message to get the correct media context
            msg = await bot.get_messages(int(chat_id), message_id)
            if not msg.empty:
                async for chunk in bot.stream_media(msg):
                    yield chunk
        except Exception as e:
            logger.error(f"Stream Error: {e}")

    # Set timeout to None so Quart doesn't kill the stream for large files
    response = await app.make_response(Response(generate(), mimetype="video/mp4"))
    response.timeout = None 
    return response

# --- Pyrogram Handlers ---
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("🚀 **Streaming Bot Ready!**\nSend a video to begin.")

@bot.on_message((filters.video | filters.document) & filters.private)
async def handle_video(client, message):
    link = f"{DOMAIN}/stream/{message.id}?chat={message.chat.id}"
    await message.reply_text(f"🎥 **Stream Link:**\n`{link}`")

# --- Main Execution ---
async def main():
    # Start the Pyrogram bot first
    await bot.start()
    logger.info("Bot started successfully.")
    
    # If you don't have a session string yet, print it to the logs once
    if not SESSION_STRING:
        string = await bot.export_session_string()
        logger.info(f"SAVE THIS SESSION STRING: {string}")

    # Run the Quart app and Pyrogram idle concurrently
    # This prevents the web server from blocking Pyrogram updates
    await asyncio.gather(
        app.run_task(host='0.0.0.0', port=PORT),
        idle()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
        
