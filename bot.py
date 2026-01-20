import os
import asyncio
from pyrogram import Client, filters
from quart import Quart, Response, request, stream_with_context

# --- Setup ---
API_ID = int(os.environ.get("API_ID", 27479878))
API_HASH = os.environ.get("API_HASH", "05f8dc8265d4c5df6376dded1d71c0ff")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DOMAIN = os.environ.get("DOMAIN", "international-angelia-uhhy5-754bbc99.koyeb.app")
PORT = int(os.environ.get("PORT", 8080))

app = Quart(__name__)
# We use in_memory=True to avoid session file issues on Koyeb's ephemeral disk
bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

@app.route('/')
async def health():
    return "Bot is Alive!", 200

# Explicit Start Command
@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text("👋 I am awake! Send me a video to get a stream link.")

# Link Generation
@bot.on_message(filters.video | filters.document)
async def handle_media(client, message):
    stream_url = f"https://{DOMAIN}/stream/{message.id}"
    await message.reply_text(f"🎥 **Stream Link:**\n`{stream_url}`")

@app.route('/stream/<int:message_id>')
async def stream_video(message_id):
    async def generate():
        async for chunk in bot.stream_media(str(message_id)):
            yield chunk
    return Response(stream_with_context(generate()), mimetype="video/mp4")

async def main():
    # Important: Start the bot before the web server
    await bot.start()
    await app.run_task(host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    asyncio.run(main())
