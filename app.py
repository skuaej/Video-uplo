import asyncio
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pyrogram import Client, filters

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
    in_memory=True
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

# STREAM ENDPOINT (RANGE FIXED)
@app.get("/stream/{file_id}")
async def stream(file_id: str, request: Request):
    try:
        file = await bot.get_file(file_id)
        tg_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"

        headers = {}
        range_header = request.headers.get("range")

        if range_header:
            headers["Range"] = range_header

        r = requests.get(tg_url, headers=headers, stream=True)

        resp_headers = {
            "Content-Type": r.headers.get("Content-Type", "video/mp4"),
            "Accept-Ranges": "bytes"
        }

        if "Content-Range" in r.headers:
            resp_headers["Content-Range"] = r.headers["Content-Range"]
            resp_headers["Content-Length"] = r.headers["Content-Length"]
            status_code = 206
        else:
            resp_headers["Content-Length"] = r.headers.get("Content-Length")
            status_code = 200

        return StreamingResponse(
            r.iter_content(chunk_size=1024 * 512),
            status_code=status_code,
            headers=resp_headers
        )

    except Exception as e:
        print("STREAM ERROR:", e)
        raise HTTPException(status_code=404, detail="Not found")

# /start
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text(
        "👋 Welcome!\n\n"
        "📤 Send me a video\n"
        "🔗 I will give you a stream link"
    )

# VIDEO HANDLER
@bot.on_message(filters.video & filters.private)
async def private_video(client, message):
    try:
        file_id = message.video.file_id
        link = f"{DOMAIN}/stream/{file_id}"
        await message.reply_text(f"🎬 Stream Link:\n{link}")
    except Exception as e:
        print("BOT ERROR:", e)
        await message.reply_text("❌ Failed to generate link")
