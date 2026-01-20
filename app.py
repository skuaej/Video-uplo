import asyncio
import requests
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pyrogram import Client, filters

API_ID = 27479878
API_HASH = "05f8dc8265d4c5df6376dded1d71c0ff"
BOT_TOKEN = "8450152940:AAHZQhivM9M5Ww66k7hu0CLQRaB30_EpJWc"
DOMAIN = "https://worldwide-beverlie-uhhy5-ae3c42ab.koyeb.app"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_file_path(file_id):
    r = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
    return r["result"]["file_path"]

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

# 🔥 STREAM + DOWNLOAD ENDPOINT
@app.get("/stream/{file_id}")
async def stream(file_id: str, request: Request):
    file_path = get_file_path(file_id)
    tg_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    r = requests.get(tg_url, stream=True)

    return StreamingResponse(
        r.iter_content(chunk_size=1024 * 512),
        media_type="video/mp4",
        headers={
            "Content-Disposition": "inline",
            "Accept-Ranges": "bytes"
        }
    )

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text(
        "👋 Send a video\n"
        "I will give you a stream + download link"
    )

@bot.on_message(filters.video & filters.private)
async def private_video(client, message):
    file_id = message.video.file_id
    link = f"{DOMAIN}/stream/{file_id}"
    await message.reply_text(f"🎬 Stream + Download:\n{link}")
