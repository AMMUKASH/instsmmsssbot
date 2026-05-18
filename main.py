import asyncio
from fastapi import FastAPI
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# --- CONFIGURATION (UPDATED TOKEN) ---
API_ID = 38138069        
API_HASH = "2ed313ebcc45cbcf65d1fc736ec71681"  
BOT_TOKEN = "8346782187:AAEjgCRs-wAE1fzV-zOqpjB_PaldyOCwDEc" # Naya Token Updated
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

app = FastAPI()

# Bot initialize karne ka safe tarika takia python 3.14 crash na kare
bot = None

async def init_bot():
    global bot
    if bot is None:
        bot = Client("insta_mms_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
        
        # Handlers ko programmatically register karna taaki decorator loop error na de
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
                    caption="👋 **Welcome!**\n\nBot ko use karne ke liye aapko hamare sabhi channels ko join karna padega.\n\nNeeche diye gaye sabhi buttons par click karke join karein 👇",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            else:
                await message.reply_photo(photo=START_IMG, caption="ʙꜱ ʏʀ ᴀʙ ᴋʏᴀ ᴊᴀᴀɴ ʟᴇɢᴀ💋")

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
                await client.send_photo(chat_id=callback_query.message.chat.id, photo=START_IMG, caption="ʙꜱ ʏʀ ᴀʙ ᴋʏᴀ ᴊᴀᴀɴ ʟᴇɢᴀ💋")

        await bot.start()
        print("🤖 Bot successfully started under running loop!")

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

@app.on_event("startup")
async def startup_event():
    # Loop generate hone ke BAAD bot ko trigger karega
    asyncio.create_task(init_bot())

@app.get("/")
def hello_world():
    return {"status": "Bot is running 24/7"}
