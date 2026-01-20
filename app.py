import os
import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

API_ID = 27479878
API_HASH = "05f8dc8265d4c5df6376dded1d71c0ff"
BOT_TOKEN = "PUT_YOUR_REAL_BOT_TOKEN"

app = FastAPI()

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


@app.get("/")
async def root():
    return {"status": "alive"}


@app.get("/stream/{file_id}")
async def stream(file_id: str):
    try:
        # Step 1: getFile
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/getFile?file_id={file_id}") as resp:
                data = await resp.json()

                if not data.get("ok"):
                    raise HTTPException(status_code=404, detail="File not found")

                file_path = data["result"]["file_path"]

        # Step 2: redirect to Telegram CDN
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        return RedirectResponse(file_url)

    except Exception as e:
        print("STREAM ERROR:", e)
        raise HTTPException(status_code=404, detail="Streaming failed")
