import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pyrogram import Client, filters

API_ID = 27479878
API_HASH = "05f8dc8265d4c5df6376dded1d71c0ff"
BOT_TOKEN = "PUT_YOUR_REAL_BOT_TOKEN"
DOMAIN = "https://worldwide-beverlie-uhhy5-ae3c42ab.koyeb.app"

app = FastAPI()

user = Client("user", api_id=API_ID, api_hash=API_HASH)
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_event("startup")
async def startup():
    # start both clients
    await user.start()
    await bot.start()

    # keep bot alive
    loop = asyncio.get_event_loop()
    loop.create_task(bot.idle())

    print("🚀 Bot + Server started")

@app.on_event("shutdown")
async def shutdown():
    await user.stop()
    await bot.stop()

@app.get("/")
async def root():
    return {"status": "alive"}

@app.get("/uploads/myfiless/id/{file_id}.mp4")
async def stream(file_id: int, request: Request):
    try:
        msg = await user.get_messages("me", file_id)
        stream = await user.stream_media(msg)

        headers = {
            "Content-Type": "video/mp4",
            "Accept-Ranges": "bytes"
        }

        return StreamingResponse(stream, headers=headers)
    except Exception as e:
        print("STREAM ERROR:", e)
        raise HTTPException(status_code=404, detail="Not found")

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text(
        "👋 Bot alive!\n\n"
        "📤 Send me a video\n"
        "🔗 I will give you a permanent stream link"
    )

@bot.on_message(filters.video & filters.private)
async def private_video(client, message):
    try:
        msg = await message.forward("me")
        link = f"{DOMAIN}/uploads/myfiless/id/{msg.id}.mp4"
        await message.reply_text(f"🎬 Stream Link:\n{link}")
    except Exception as e:
        print("BOT ERROR:", e)
        await message.reply_text("❌ Failed to generate link")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
