from fastapi import FastAPI
from pyrogram import Client, filters
import requests

API_ID = 27479878
API_HASH = "05f8dc8265d4c5df6376dded1d71c0ff"
BOT_TOKEN = "PUT_YOUR_REAL_BOT_TOKEN"

app = FastAPI()

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_file_link(file_id):
    r = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
    file_path = r["result"]["file_path"]
    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

@app.on_event("startup")
async def startup():
    await bot.start()

@app.on_event("shutdown")
async def shutdown():
    await bot.stop()

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text("👋 Bot alive!\nSend video for link")

@bot.on_message(filters.video & filters.private)
async def private_video(client, message):
    file_id = message.video.file_id
    link = get_file_link(file_id)
    await message.reply_text(f"🎬 Link:\n{link}")
