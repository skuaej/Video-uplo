import os
import asyncio
import logging
from pyrogram import Client, filters, idle
from quart import Quart, Response, request, stream_with_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Config ---
API_ID = int(os.environ.get("API_ID", 27479878))
API_HASH = os.environ.get("API_HASH", "05f8dc8265d4c5df6376dded1d71c0ff")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", None) # Optional but highly recommended
DOMAIN = os.environ.get("DOMAIN", "international-angelia-uhhy5-754bbc99.koyeb.app")
PORT = int(os.environ.get("PORT", 8000))

app = Quart(__name__)

# If you have a session string, it bypasses the constant DC migration logs
if SESSION_STRING:
    bot = Client("stream_bot", session_string=SESSION_STRING, in_memory=True)
else:
    bot = Client("stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

@app.route('/')
async def health():
    return "Bot is Streaming!", 200

@app.route('/stream/<int:message_id>')
async def stream_video(message_id):
    chat_id = request.args.get("chat")
    @stream_with_context
    async def generate():
        try:
            # We fetch the message to get the correct media context
            msg = await bot.get_messages(int(chat_id), message_id)
            async for chunk in bot.stream_media(msg):
                yield chunk
        except Exception as e:
            logger.error(f"Stream Error: {e}")

    return Response(generate(), mimetype="video/mp4")

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("🚀 **Streaming Bot Ready!**\nSend a video to begin.")

@bot.on_message((filters.video | filters.document) & filters.private)
async def handle_video(client, message):
    link = f"https://{DOMAIN}/stream/{message.id}?chat={message.chat.id}"
    await message.reply_text(f"🎥 **Stream Link:**\n`{link}`")

async def main():
    await bot.start()
    logger.info("Bot started successfully.")
    
    # If you don't have a session string yet, print it to the logs once
    if not SESSION_STRING:
        string = await bot.export_session_string()
        logger.info(f"SAVE THIS SESSION STRING: {string}")

    loop = asyncio.get_event_loop()
    loop.create_task(app.run_task(host='0.0.0.0', port=PORT))
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
