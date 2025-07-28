import os
import asyncio
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

app = Client("uploader-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def download_file(session, url, filename):
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filename, "wb") as f:
                    f.write(await resp.read())
                return filename
    except Exception as e:
        print(f"Download error: {e}")
    return None

@app.on_message(filters.document & filters.private)
async def handler(client, message: Message):
    if message.document.mime_type == "text/plain":
        txt_path = await message.download()
        links = [line.strip() for line in open(txt_path) if line.strip()]
        await message.reply(f"✅ Found {len(links)} links. Processing...")
        async with aiohttp.ClientSession() as session:
            for url in links:
                fname = url.split("/")[-1].split("?")[0]
                path = await download_file(session, url, fname)
                if path:
                    await app.send_document(chat_id=CHAT_ID, document=path, caption=fname)
                    os.remove(path)

app.run()
