import os
import asyncio
from pyrogram import Client, filters
from quart import Quart, Response, request, stream_with_context

# --- Configuration (Set these in Koyeb Env Vars) ---
API_ID = int(os.environ.get("API_ID", 27479878))
API_HASH = os.environ.get("API_HASH", "05f8dc8265d4c5df6376dded1d71c0ff")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DOMAIN = os.environ.get("DOMAIN", "international-angelia-uhhy5-754bbc99.koyeb.app")
PORT = int(os.environ.get("PORT", 8080))

app = Quart(__name__)
bot = Client("stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.route('/')
async def health():
    return "Streaming Bot is Online", 200

@app.route('/stream/<int:message_id>')
async def stream_video(message_id):
    # This gets the video directly from Telegram's servers
    async def generate():
        async for chunk in bot.stream_media(str(message_id)):
            yield chunk

    return Response(
        stream_with_context(generate()),
        mimetype="video/mp4",
        headers={"Content-Disposition": "inline"} # Tells browser to play, not download
    )

@bot.on_message(filters.video | filters.document)
async def handle_media(client, message):
    # We use message.id to identify the file
    stream_url = f"https://{DOMAIN}/stream/{message.id}"
    await message.reply_text(
        f"🎥 **Link Generated!**\n\n"
        f"🔗 `{stream_url}`\n\n"
        f"⚠️ *Note: On Free Tier, links may time out after 2 minutes.*"
    )

async def main():
    await bot.start()
    # Quart runs the web server that Koyeb needs for health checks
    await app.run_task(host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    asyncio.run(main())
