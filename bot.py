import os
import asyncio
import logging
from pyrogram import Client, filters, types
from quart import Quart, request, Response, stream_with_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Config ---
API_ID = int(os.environ.get("API_ID", 27479878))
API_HASH = os.environ.get("API_HASH", "05f8dc8265d4c5df6376dded1d71c0ff")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DOMAIN = os.environ.get("DOMAIN", "international-angelia-uhhy5-754bbc99.koyeb.app")
PORT = int(os.environ.get("PORT", 8080))

app = Quart(__name__)
bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

@app.before_serving
async def startup():
    await bot.start()
    # Set the Webhook so Telegram knows where to send messages
    webhook_url = f"https://{DOMAIN}/webhook"
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

@app.route('/webhook', methods=['POST'])
async def telegram_webhook():
    # Receive update from Telegram
    data = await request.get_json()
    update = types.Update.all_from_dict(data)
    # Manually feed the update to Pyrogram's dispatcher
    await bot.dispatcher.process_update(update)
    return "OK", 200

@app.route('/')
async def health():
    return "Bot is Alive!", 200

# --- Bot Handlers ---
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text("🚀 **Webhook Mode Active!**\nSend a video for a link.")

@bot.on_message((filters.video | filters.document) & filters.private)
async def handle_media(client, message):
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
            logger.error(f"Stream error: {e}")
    return Response(generate(), mimetype="video/mp4")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
