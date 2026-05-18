import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import uvicorn

# --- CONFIGURATION ---
API_ID = 38138069        
API_HASH = "2ed313ebcc45cbcf65d1fc736ec71681"  
BOT_TOKEN = "8469456367:AAHnPUxDa1246b3O4p0yHkM4CKkIfSsToW0" 
START_IMG = "https://files.catbox.moe/ko5i86.jpg"

CHANNELS = [
    {"name": "ɪɴᴅɪᴀɴ ᴍᴍꜱ💋", "username": "About_Genious"},
    {"name": "ʀᴇᴀʟ ʜɪɴᴅɪ ᴍᴍꜱ💋", "username": "Tele_links_update"},
    {"name": "ꜰᴏʀᴄᴇ ꜰᴜᴄᴋ💋", "username": "Seling_Proff"},
    {"name": "ᴍᴏᴍ & ꜱᴏɴ💋💋", "username": "Genu_Bot_Support"},
    {"name": "ᴄʜɪʟᴅ ꜱᴇx💋💋", "username": "Friend_Forevr"},
    {"name": "ꜱᴛᴇᴩ ᴍᴏᴍ ꜱᴏɴ💋💋", "username": "SticrAura"},
    {"name": "ꜱᴄʜᴏᴏʟ ɪɴᴅɪᴀɴ ɢɪʀʟ💋💋", "username": "Villain_Loves"},
    {"name": "ɪɴᴅɪᴀɴ ᴅᴇꜱɪ ᴀᴜɴᴛʏ💋💋", "username": "Sexi_Aura"},
    {"name": "ʙʜᴀʙʜɪ ʟᴏᴠᴇ💋💋", "username": "Usertag_update"},
    {"name": "ᴊᴀᴩᴀɴᴇᴇꜱ ɢɪʀʟ💋💋💋", "username": "MoviesHub_Verse"},
    {"name": "ʀᴇᴀʟ ᴍᴍꜱ ᴠɪʀᴀʟ💋💋", "username": "K8vin_Hub"},
    {"name": "ᴠɪʀᴀʟ ᴠɪᴅᴇᴏꜱ💋💋💋", "username": "Animyedit"},
    {"name": "ꜱᴜɴɴʏ ʟᴇᴏɴᴇ💋💋", "username": "ll_CEO_OF_YOO_ll"}
]
# --------------------------------------------

# Pyrogram Bot Initialize (Bina loop ke taaki error na aaye)
bot = Client("insta_mms_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- MODERN LIFESPAN MANAGER (Event Loop Fix) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI start hote hi pehle bot start hoga (Same event loop me)
    print("🤖 Starting Telegram Bot...")
    await bot.start()
    print("🤖 @Insta_mmmmmsss_bot is now active!")
    yield
    # FastAPI stop hote hi bot stop ho jayega
    print("🤖 Stopping Bot...")
    await bot.stop()

# FastAPI App with Lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/")
def hello_world():
    return {"status": "Bot is running 24/7", "username": "@Insta_mmmmmsss_bot"}

# --- BOT LOGIC ---
async def check_user_joined(client, user_id):
    not_joined = []
    for channel in CHANNELS:
        try:
            await client.get_chat_member(channel["username"], user_id)
        except UserNotParticipant:
            not_joined.append(channel)
        except Exception:
            continue
    return not_joined

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    not_joined_channels = await check_user_joined(client, user_id)
    
    if not_joined_channels:
        buttons = []
        row = []
        for channel in not_joined_channels:
            row.append(InlineKeyboardButton(text=channel['name'], url=f"https://t.me/{channel['username']}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
            
        buttons.append([InlineKeyboardButton(text="🔄 Checked / Try Again", callback_data="check_again")])
        
        await message.reply_photo(
            photo=START_IMG,
            caption=(
                "👋 **Welcome!**\n\n"
                "Bot ko use karne ke liye aapko hamare sabhi channels ko join karna padega.\n"
                "Neeche diye gaye sabhi buttons par click karke join karein 👇"
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await message.reply_photo(
            photo=START_IMG,
            caption="ʙꜱ ʏʀ ᴀʙ ᴋʏᴀ ᴊᴀᴀɴ ʟᴇɢᴀ💋"
        )

@bot.on_callback_query(filters.regex("check_again"))
async def check_again_callback(client, callback_query):
    user_id = callback_query.from_user.id
    not_joined_channels = await check_user_joined(client, user_id)
    
    if not_joined_channels:
        await callback_query.answer(text="❌ Aapne abhi bhi saare channels join nahi kiye hain! Kripya sabhi ko join karein.", show_alert=True)
    else:
        await callback_query.answer("✅ Verification successful!", show_alert=False)
        try:
            await callback_query.message.delete()
        except Exception:
            pass
            
        await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=START_IMG,
            caption="ʙꜱ ʏʀ ᴀʙ ᴋʏᴀ ᴊᴀᴀɴ ʟᴇɢᴀ💋"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
