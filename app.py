import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 27479878
API_HASH = "05f8dc8265d4c5df6376dded1d71c0ff"
BOT_TOKEN = "PUT_YOUR_REAL_BOT_TOKEN"
DOMAIN = "https://worldwide-beverlie-uhhy5-ae3c42ab.koyeb.app"

app = FastAPI()

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=5,
)

@app.on_event("startup")
async def startup():
    await bot.start()
    print("🚀 Bot started")

@app.on_event("shutdown")
async def shutdown():
    await bot.stop()

@app.get("/")
async def root():
    return {"status": "alive"}

# STREAM ENDPOINT
@app.get("/stream/{file_id}")
async def stream(file_id: str):
    try:
        # Telegram file_id se stream
        async def generator():
            async for chunk in bot.stream_media(file_id):
                yield chunk

        headers = {
            "Content-Type": "video/mp4",
            "Accept-Ranges": "bytes"
        }

        return StreamingResponse(generator(), headers=headers)

    except Exception as e:
        print("STREAM ERROR:", e)
        raise HTTPException(status_code=404, detail="Not found")


# /start command
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    await message.reply_text(
        "👋 Send me a video\n"
        "I will give you a direct stream link"
    )


# VIDEO HANDLER
@bot.on_message(filters.video & filters.private)
async def video_handler(client: Client, message: Message):
    try:
        file_id = message.video.file_id
        link = f"{DOMAIN}/stream/{file_id}"

        await message.reply_text(
            f"🎬 **Your Stream Link:**\n{link}",
            disable_web_page_preview=False
        )

    except Exception as e:
        print("BOT ERROR:", e)
        await message.reply_text("❌ Failed to generate stream link")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
