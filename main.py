import os
import random
import aiohttp
import asyncio
from PIL import Image
from io import BytesIO
from pyrogram import Client, filters
from keep_alive import keep_alive

API_ID = 34135757
API_HASH = "d3d5548fe0d98eb1fb793c2c37c9e5c8"
BOT_TOKEN = "8442588313:AAHITlgOAQ6_kUqk9ShvC_KS04t-rNg-dmA"

START_IMG = "https://graph.org/file/465913059119da96c4113-ddfa7acbeed879d51c.jpg"

OWNER = 8581811595
LOG_GROUP = -1003867805165

app = Client("pfp_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# SEARCH CATEGORIES
CATEGORIES = {
    "boys": "boys pfp aesthetic",
    "girls": "girls pfp aesthetic",
    "anime": "anime girl boy pfp",
    "couple": "couple aesthetic pfp",
    "cute": "cute pfp aesthetic",
    "dark": "dark black aesthetic pfp",
}

# FETCH IMAGES
async def get_images(q):
    urls = []
    search_url = f"https://lexica.art/api/v1/search?q={q}"
    async with aiohttp.ClientSession() as s:
        async with s.get(search_url) as r:
            data = await r.json()
            for i in data["images"]:
                urls.append(i["src"])
    return urls[:50]

# CROP IMAGE 1:1
def crop_square(img):
    w, h = img.size
    s = min(w, h)
    left = (w - s) // 2
    top = (h - s) // 2
    return img.crop((left, top, left + s, top + s))

# START COMMAND
@app.on_message(filters.command("start"))
async def start(_, m):
    await m.reply_photo(
        START_IMG,
        caption=(
            "✨ **ʀᴜᴍᴀ ᴀʟʟ ᴘꜰᴘ ʙᴏᴛ** ✨\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👦 **Boys** | 👧 **Girls**\n"
            "🎎 **Anime** | 💑 **Couple**\n"
            "✨ **Cute** | 🌙 **Dark**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💜 **Type anything like:**\n"
            "• boys pfp\n"
            "• girls pfp\n"
            "• anime pfp\n"
            "• couple pfp\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔥 **50 HD Pics per request**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📢 **Update:** @radhesupport\n"
            "🛠️ **Support Group:** https://t.me/+PKYLDIEYiTljMzMx\n"
            "👑 **Owner:** @SweetRuma\n"
            "🆔 **Owner UserID:** `8581811595`\n"
            "🗂️ **Log Group:** `-1003867805165`\n"
        ),
    )

# AUTO DETECT MESSAGE & SEND PICS
@app.on_message(filters.text & ~filters.command(["start"]))
async def fetch(_, m):
    q = m.text.lower()
    key = None

    for k in CATEGORIES:
        if k in q:
            key = k

    if not key:
        key = "girls"

    await m.reply("🔍 Fetching **50 HD PFPs…** Please wait 🔥")

    urls = await get_images(CATEGORIES[key])

    # SEND IN 10x5 BATCHES
    for i in range(0, 50, 10):
        batch = urls[i:i+10]
        media = []

        for link in batch:
            async with aiohttp.ClientSession() as s:
                async with s.get(link) as r:
                    img_bytes = await r.read()
                    img = Image.open(BytesIO(img_bytes))
                    img = crop_square(img)

                    buf = BytesIO()
                    buf.name = "pfp.jpg"
                    img.save(buf, "JPEG")
                    buf.seek(0)
                    media.append(buf)

        for p in media:
            await m.reply_photo(p)

    # LOGGING
    await app.send_message(LOG_GROUP, f"User {m.from_user.id} requested → {q}")

print("Bot Running...")
keep_alive()
app.run()
