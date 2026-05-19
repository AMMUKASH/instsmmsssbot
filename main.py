import asyncio
import re
import nest_asyncio  # Latest Python Event Loop Crash Fix

# Pyrogram Client init hone se pehle apply karna compulsory hai
nest_asyncio.apply()

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatPermissions
from config import Config
import database as db
from aiohttp import web

bot = Client(
    "GuardianProBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# --- CONFIG HARDCODED VALUES FOR LOGS, OWNER & LINKS ---
LOG_GROUP_ID = -1003947649552
OWNER_USERNAME = "CoderNova"
UPDATE_CHANNEL_LINK = "https://t.me/Gc_help_update"
SUPPORT_GROUP_LINK = "https://t.me/Genu_Bot_Support"
BOT_USERNAME = "Group_secu_bot"

# Bad words list for Anti Abuse Filter
BAD_WORDS = ["bhenchod", "madarchod", "gand", "chutiya", "luda", "lavda", "bsdk", "harami", "randi", "sala"]

# NSFW aur Drugs detect karne ke liye strict blacklisted text/caption tags
NSFW_DRUG_KEYWORDS = [
    "nsfw", "18+", "porn", "xxx", "sex", "nude", "naked", "pussy", "dick",
    "drugs", "weed", "ganja", "cocaine", "charas", "heroin", "mdma", "pills"
]

# --- WEB SERVER SETUP FOR RENDER PORT BINDING ---
async def handle(request):
    return web.Response(text="Bot is Running and Alive 24/7!")

async def start_server():
    try:
        app = web.Application()
        app.router.add_get('/', handle)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', Config.PORT)
        await site.start()
        print("🌐 WEB SERVER ACTIVE ON PORT CONFIGURATION!")
    except Exception as e:
        print(f"⚠️ Web Server Error: {e}")

# --- HELPER FUNCTIONS ---
async def extract_user(client, message: Message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    if len(message.command) < 2:
        return None
    user_to_find = message.command[1]
    if user_to_find.isdigit():
        try: return await client.get_users(int(user_to_find))
        except: return None
    if user_to_find.startswith("@"):
        user_to_find = user_to_find.replace("@", "")
    try: return await client.get_users(user_to_find)
    except: return None

def parse_buttons(text):
    if not text: return None
    try:
        kb = []
        matches = re.findall(r'\[([^\]]+)\|([^\]]+)\]', text)
        for name, url in matches:
            kb.append([InlineKeyboardButton(name.strip(), url=url.strip())])
        return kb if kb else None
    except: return None

async def is_admin(chat, user_id):
    if chat.type.value in ["private"]: return True
    try:
        m = await bot.get_chat_member(chat.id, user_id)
        return m.status.value in ["administrator", "owner"]
    except: return False

def get_action_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ ✨", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
            InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇ", url=UPDATE_CHANNEL_LINK)
        ]
    ])

# --- TEXT TEMPLATES FOR DYNAMIC SECTIONS (STYLISH FONTS) ---
START_TEXT = (
    "⚡ **ʜᴇʟʟᴏ {name}!**\n\n"
    "🛡️ **ɪ ᴀᴍ ɢᴜᴀʀᴅɪᴀɴ ᴘʀᴏ**, ʏᴏᴜʀ ᴜbʟᴛɪᴍᴀᴛᴇ ɢʀᴏᴜᴘ sᴇᴄᴜʀɪᴛʏ ᴀɴᴅ ᴍᴏᴅᴇʀᴀᴛɪᴏɴ ᴀssɪsᴛᴀɴᴛ.\n\n"
    "ɪ ᴄᴀɴ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ᴄʜᴀᴛs ғʀᴏᴍ sᴘᴀᴍᴍᴇʀs, ɴsғᴡ ᴍᴇᴅɪᴀ, ᴀʙᴜsɪᴠᴇ ʟᴀɴɢᴜᴀɢᴇ, ᴀɴᴅ ᴜɴᴡᴀɴᴛᴇᴅ ʟɪɴᴋs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ.\n\n"
    "📌 **#ɴᴏᴛᴇ:** ᴀᴀᴘ ᴅɪʀᴇᴄᴛ `/setting` ᴄᴏᴍᴍᴀɴᴅ ᴜsᴇ ᴋᴀʀᴋᴇ ʙʜɪ sᴀᴀʀᴇ sᴇᴄᴜʀɪᴛʏ ғᴇᴀᴛᴜʀᴇs ᴀᴜr ᴜɴᴋɪ ɢᴜɪᴅᴇs ᴏᴘᴇɴ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ.\n\n"
    "👤 **ᴅᴇᴠᴇʟᴏᴘᴇʀ:** @{owner}"
)

START_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✨", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
    [
        InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇs", url=UPDATE_CHANNEL_LINK),
        InlineKeyboardButton("👥 sᴜᴘᴘᴏʀᴛ", url=SUPPORT_GROUP_LINK)
    ],
    [InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢ ᴍᴇɴᴜ", callback_data="modules_menu")]
])

SETTING_MENU_TEXT = (
    "⚙️ **ɢᴜᴀʀᴅɪᴀɴ ᴘʀᴏ - sᴇᴄᴜʀɪᴛʏ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴs**\n\n"
    "ɴɪᴄʜᴇ ᴅɪʏᴇ ɢᴀʏᴇ ʙᴜᴛᴛᴏɴs ᴘᴀʀ ᴄʟɪᴄᴋ ᴋᴀʀᴋᴇ ᴀᴀᴘ ʜᴀʀ ᴇᴋ sᴇᴄᴜʀɪᴛʏ ᴍᴏᴅᴜʟᴇ ᴋɪ **ᴡᴏʀᴋɪɴɢ, ɢᴜɪᴅᴇ, ᴀᴜʀ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs** ᴄʜᴇᴄᴋ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ:"
)

SETTING_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="guide_link"),
        InlineKeyboardButton("🔞 ɴsғᴡ & ᴅʀᴜɢs", callback_data="guide_nsfw")
    ],
    [
        InlineKeyboardButton("🚫 ᴀɴᴛɪ-ᴀʙᴜsᴇ", callback_data="guide_abuse"),
        InlineKeyboardButton("📥 ғᴏʀᴡᴀʀᴅ ᴄᴛʀʟ", callback_data="guide_forward")
    ],
    [
        InlineKeyboardButton("🛡️ ʙɪᴏ & ᴇᴅɪᴛ ɢᴜᴀʀᴅ", callback_data="guide_bio"),
        InlineKeyboardButton("🛠️ ᴀᴅᴍɪɴ ᴄᴍᴅs", callback_data="guide_admin")
    ],
    [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="back_start")]
])

# --- DYNAMIC SECURITY WARN & MUTE HANDLER ---
async def handle_member_violation(client, message: Message, target_user, reason):
    chat_id = message.chat.id
    count = await db.add_warn(chat_id, target_user.id)
    
    if count >= 3:
        try:
            await client.restrict_chat_member(
                chat_id, 
                target_user.id, 
                permissions=ChatPermissions(can_send_messages=False),
                until_date=int(asyncio.get_event_loop().time() + 1800)
            )
            await db.reset_warns(chat_id, target_user.id)
            mute_text = f"🤐 {target_user.mention} ko **3/3 Warnings** exceed karne par **30 Mins** ke liye mute kar diya gaya.\n\n⚠️ **Reason:** {reason}"
            await message.reply_text(mute_text, reply_markup=get_action_buttons())
            
            if LOG_GROUP_ID:
                await client.send_message(LOG_GROUP_ID, f"🤐 **#AUTO_MUTE_REPORT**\n\n💬 **ɢʀᴏᴜᴘ:** {message.chat.title}\n👤 **ᴜsᴇʀ:** {target_user.mention}\n⚠️ **ʀᴇᴀsᴏɴ:** {reason} (3/3 Warns)")
        except Exception as e:
            print(f"Mute Error: {e}")
    else:
        warn_text = f"⚠️ {target_user.mention} ko warning di gayi! (**{count}/3**)\n\n🚫 **Reason:** {reason}"
        await message.reply_text(warn_text, reply_markup=get_action_buttons())
        
        if LOG_GROUP_ID:
            await client.send_message(LOG_GROUP_ID, f"⚠️ **#AUTO_WARN_REPORT**\n\n💬 **ɢʀᴏᴜᴘ:** {message.chat.title}\n👤 **ᴜsᴇʀ:** {target_user.mention}\n📊 **ᴡᴀʀɴs:** {count}/3\n🚫 **ʀᴇᴀsᴏɴ:** {reason}")


# --- COMMAND HANDLERS ---

@bot.on_message(filters.command(["start", f"start@{BOT_USERNAME}"]))
async def start_cmd(client, message: Message):
    try:
        if message.chat.type.value == "private":
            await db.add_served_user(message.chat.id)
        else:
            await db.add_served_chat(message.chat.id)
    except Exception as e:
        print(f"Database Tracking Error: {e}")

    text = START_TEXT.format(name=message.from_user.first_name, owner=OWNER_USERNAME)
    try:
        await message.reply_photo(photo=Config.START_IMG, caption=text, reply_markup=START_BUTTONS)
    except Exception:
        await message.reply_text(text, reply_markup=START_BUTTONS)

    if LOG_GROUP_ID:
        try:
            log_text = f"🔔 **#START_TRIGGERED**\n\n👤 **ᴜsᴇʀ:** {message.from_user.mention}\n💬 **ᴄʜᴀᴛ:** {message.chat.title or 'Private'}"
            await client.send_message(LOG_GROUP_ID, log_text)
        except: pass


@bot.on_message(filters.command(["setting", f"setting@{BOT_USERNAME}"]))
async def setting_cmd(client, message: Message):
    if message.chat.type.value != "private":
        if not await is_admin(message.chat, message.from_user.id):
            await message.reply_text("❌ Is command ko use karne ke liye aapka Group Admin hona zaroori hai!")
            return
            
    try:
        await message.reply_photo(
            photo=Config.START_IMG, 
            caption=SETTING_MENU_TEXT, 
            reply_markup=SETTING_BUTTONS
        )
    except Exception:
        await message.reply_text(SETTING_MENU_TEXT, reply_markup=SETTING_BUTTONS)


# --- 🎮 INTERACTIVE CALLBACK MENU SYSTEM (STYLISH GUIDES) 🎮 ---

@bot.on_callback_query()
async def cb_handler(client, cb: CallbackQuery):
    data = cb.data
    
    if data == "modules_menu" or data == "back_modules":
        await cb.message.edit_caption(caption=SETTING_MENU_TEXT, reply_markup=SETTING_BUTTONS)

    elif data == "back_start":
        text = START_TEXT.format(name=cb.from_user.first_name, owner=OWNER_USERNAME)
        await cb.message.edit_caption(caption=text, reply_markup=START_BUTTONS)

    # 1. Anti-Link Guide
    elif data == "guide_link":
        guide = (
            "🔗 ╔════════════════════╗\n"
            "      **ᴀɴᴛɪ-ʟɪɴᴋ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ**\n"
            "╚════════════════════╝\n\n"
            "● **ᴡᴏʀᴋɪɴɢ:** ᴊᴀʙ ʙʜɪ ᴋᴏɪ ɴᴏɴ-ᴀᴅᴍɪɴ ᴍᴇᴍʙᴇʀ ɢʀᴏᴜᴘ ᴍᴇɪɴ ᴋɪsɪ ᴡᴇʙsɪᴛᴇ, ᴄʜᴀɴɴᴇʟ, ʏᴀ ᴛᴇʟᴇɢʀᴀᴍ ɪɴᴠɪᴛᴇ ʟɪɴᴋ (`t.me`, `http`) ʙʜᴇᴊᴇɢᴀ, ʙᴏᴛ ᴜsᴇ ɪɴsᴛᴀɴᴛʟʏ ᴅᴇʟᴇᴛᴇ ᴋᴀʀ ᴅᴇɢᴀ.\n\n"
            "● **ᴘᴇɴᴀʟᴛʏ:** ᴍᴇᴍʙᴇʀ ᴋᴏ **1 ᴡᴀʀɴɪɴɢ** ᴅɪ ᴊᴀʏᴇɢɪ. 3/3 ᴡᴀʀɴɪɴɢs ʜᴏɴᴇ ᴘᴀʀ ᴜsᴇʀ **30 ᴍɪɴs** ᴋᴇ ʟɪʏᴇ ᴀᴜᴛᴏ-ᴍᴜᴛᴇ ʜᴏ ᴊᴀʏᴇɢᴀ."
        )
        await cb.message.edit_caption(caption=guide, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_modules")]]))

    # 2. NSFW Guide
    elif data == "guide_nsfw":
        guide = (
            "🔞 ╔════════════════════╗\n"
            "      **ɴsғᴡ & ᴅʀᴜɢs sᴇᴄᴜʀɪᴛʏ**\n"
            "╚════════════════════╝\n\n"
            "● **ᴡᴏʀᴋɪɴɢ:** ʏᴇʜ ᴍᴏᴅᴜʟᴇ ɢʀᴏᴜᴘ ᴋᴇ ᴍᴀʜᴏʟ ᴋᴏ ᴘʀᴇᴍɪᴜᴍ ʀᴀᴋʜɴᴇ ᴋᴇ ʟɪʏᴇ ʜᴀɪ. ᴀɢᴀʀ ᴋᴏɪ ᴛᴇxᴛ, ᴄᴀᴘᴛɪᴏɴ, ʏᴀ ɪᴍᴀɢᴇ sᴘᴏɪʟᴇʀ ғɪʟᴛᴇʀ ʙʟᴀᴄᴋlistᴇᴅ sᴇɴsɪᴛɪᴠᴇ ᴡᴏʀᴅs (`nsfw`, `xxx`, `drugs`, `weed`) ᴍᴀᴛᴄʜ ᴋᴀʀᴇɢᴀ, ᴛᴏʜ ᴄᴏɴᴛᴇɴᴛ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ʜᴏ ᴊᴀʏᴇɢᴀ.\n\n"
            "● **ɴᴏᴛᴇ:** ɴᴏʀᴍᴀʟ ᴍᴇᴅɪᴀ ғɪʟᴇs (ᴘɪᴄs/ᴠɪᴅᴇᴏs) ʙɪʟᴋᴜʟ sᴀғᴇ ʀᴀʜᴇɴɢɪ."
        )
        await cb.message.edit_caption(caption=guide, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_modules")]]))

    # 3. Anti-Abuse Guide
    elif data == "guide_abuse":
        guide = (
            "🚫 ╔════════════════════╗\n"
            "      **ᴀɴᴛɪ-ᴀʙᴜsᴇ ᴍᴏɴɪᴛᴏʀ**\n"
            "╚════════════════════╝\n\n"
            "● **ᴡᴏʀᴋɪɴɢ:** ɢʀᴏᴜᴘ ᴍᴇɪɴ ɢᴀᴀʟɪ-ɢᴀʟᴏᴄʜ ᴀᴜʀ ᴀʙᴜsɪᴠᴇ ʟᴀɴɢᴜᴀɢᴇ ᴋᴏ ʀᴏᴋɴᴇ ᴋᴇ ʟɪʏᴇ ʏᴇʜ ғɪʟᴛᴇʀ 𝟸𝟺/𝟽 ᴀᴄᴛɪᴠᴇ ʀᴀʜᴛᴀ ʜᴀɪ.\n\n"
            "● **ᴀᴄᴛɪᴏɴ:** ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs ʙʜᴇᴊᴛᴇ ʜɪ ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇ ʜᴏɢᴀ ᴀᴜʀ sᴇɴᴅᴇʀ ᴋᴏ ᴡᴀʀɴɪɴɢ sʏsᴛᴇᴍ ʜɪᴛ ᴋᴀʀᴇɢᴀ."
        )
        await cb.message.edit_caption(caption=guide, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_modules")]]))

    # 4. Forward Ctrl Guide
    elif data == "guide_forward":
        guide = (
            "📥 ╔════════════════════╗\n"
            "      **ғᴏʀᴡᴀʀᴅ ᴄᴏɴᴛʀᴏʟ sʏsᴛᴇᴍ**\n"
            "╚════════════════════╝\n\n"
            "● **ᴡᴏʀᴋɪɴɢ:** ᴅᴜsʀᴇ ᴄʜᴀɴɴᴇʟs ʏᴀ ᴘʀᴏᴍᴏᴛɪᴏɴᴀʟ ɢʀᴏᴜᴘs sᴇ ᴄᴏɴᴛᴇɴᴛ ᴅɪʀᴇᴄᴛ ғᴏʀᴡᴀʀᴅ ᴋᴀʀɴᴀ ɢʀᴏᴜᴘ ᴍᴇɪɴ sᴛʀɪᴄᴛʟʏ ʙᴀɴ ʜᴀɪ.\n\n"
            "● **ᴀᴄᴛɪᴏɴ:** ɴᴏɴ-ᴀᴅᴍɪɴ ᴍᴇmʙᴇʀs ᴋᴀ ʜᴀʀ ᴇᴋ ғᴏʀᴡᴀʀᴅᴇᴅ ᴍᴇssᴀɢᴇ ʙᴏᴛ ɪɴsᴛᴀɴᴛʟʏ ᴅᴇʟᴇᴛᴇ ᴋᴀʀ ᴅᴇᴛᴀ ʜᴀɪ."
        )
        await cb.message.edit_caption(caption=guide, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_modules")]]))

    # 5. Bio & Edit Guard Guide
    elif data == "guide_bio":
        guide = (
            "🛡️ ╔════════════════════╗\n"
            "      **ʙɪᴏ & ᴇᴅɪᴛ sᴇᴄᴜʀɪᴛʏ**\n"
            "╚════════════════════╝\n\n"
            "● **ʙɪᴏ ɢᴜᴀʀᴅ:** ᴀɢᴀʀ ᴋɪsɪ ᴜsᴇʀ ᴋᴇ ᴛᴇʟᴇɢʀᴀᴍ ɢʟᴏʙᴀʟ ʙɪᴏ ᴍᴇɪɴ sᴘᴀᴍ/ᴡᴇʙsɪᴛᴇ ʟɪɴᴋ ʜᴀɪ ᴀᴜʀ ᴡᴏ ɢʀᴏᴜᴘ ᴍᴇɪɴ ᴄʜᴀᴛ ᴋᴀʀᴇɢᴀ, ᴛᴏʜ sᴇᴄᴜʀɪᴛʏ ᴀʟᴇʀᴛ ᴛʀɪɢɢᴇʀ ʜᴏ ᴊᴀʏᴇɢᴀ.\n\n"
            "● **ᴇᴅɪᴛ ɢᴜᴀʀᴅ:** ᴀɢᴀʀ ᴋᴏɪ ᴍᴇʙᴇʀ ᴘᴇʜʟᴇ ɴᴏʀᴍᴀʟ ᴍᴇssᴀɢᴇ ʙʜᴇᴊ ᴋᴀʀ ʙᴀᴀᴅ ᴍᴇɪɴ ᴜsᴇ ᴇᴅɪᴛ ᴋᴀʀᴋᴇ ʟɪɴᴋ ᴅᴀᴀʟᴛᴀ ʜᴀɪ, ᴛᴏʜ ʙᴏᴛ ᴜsᴇ ʙʜɪ ᴅᴇʟᴇᴛᴇ ᴋᴀʀ ᴅᴇɢᴀ!"
        )
        await cb.message.edit_caption(caption=guide, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_modules")]]))

    # 6. Admin Cmds Guide
    elif data == "guide_admin":
        guide = (
            "🛠️ ╔════════════════════╗\n"
            "      **ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs ᴘᴀɴᴇʟ**\n"
            "╚════════════════════╝\n\n"
            "ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ɴɪᴄʜᴇ ᴅɪʏᴇ ɢᴀʏᴇ ᴘᴏᴡᴇʀғᴜʟ ᴄᴏᴍᴍᴀɴᴅs ᴜsᴇ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ:\n\n"
            "• `/ban` ➔ ᴍᴇᴍʙᴇʀ ᴋᴏ ᴘᴇʀᴍᴀɴᴇɴᴛʟʏ ʙʟᴏᴄᴋ ᴋᴀʀᴇɪɴ\n"
            "• `/unban` ➔ ᴍᴇᴍʙᴇʀ ᴋᴀ ʙᴀɴ ʀᴇᴍᴏᴠᴇ ᴋᴀʀᴇɪɴ\n"
            "• `/mute` ➔ ᴜsᴇʀ ᴋᴀ ᴄʜᴀᴛ ᴀᴄᴄᴇss ʙᴀɴᴅ ᴋᴀʀᴇɪɴ\n"
            "• `/unmute` ➔ ᴄʜᴀᴛ ᴀᴄᴄᴇss ᴡᴀᴘᴀs ᴋʜᴏʟᴇɪɴ\n"
            "• `/warn` ➔ ᴜsᴇʀ ᴋᴏ ᴍᴀɴᴜᴀʟ ᴡᴀʀɴɪɴɢ ᴅᴇɪɴ\n"
            "• `/diswarn` ➔ sᴀᴀʀᴇ ᴡᴀʀɴɪɴɢs ᴄʟᴇᴀɴ ᴋᴀʀᴇɪɴ\n"
            "• `/approve` ➔ ᴜsᴇʀ ᴋᴏ ᴡʜɪᴛᴇʟɪsᴛ ᴋᴀʀᴇɪɴ (ɴᴏ ғɪʟᴛᴇʀs)"
        )
        await cb.message.edit_caption(caption=guide, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_modules")]]))


# --- CORE ADMIN COMMANDS CODE (SUPPORTING EXTENDED FORMATS) ---
@bot.on_message(filters.command(["ban", "unban", "mute", "unmute", "warn", "diswarn", "approve", "disapprove",
                                 f"ban@{BOT_USERNAME}", f"unban@{BOT_USERNAME}", f"mute@{BOT_USERNAME}", f"unmute@{BOT_USERNAME}",
                                 f"warn@{BOT_USERNAME}", f"diswarn@{BOT_USERNAME}", f"approve@{BOT_USERNAME}", f"disapprove@{BOT_USERNAME}"]))
async def admin_commands_engine(client, message: Message):
    if message.chat.type.value == "private":
        await message.reply_text("❌ Yeh commands sirf Groups (Public/Private) mein kaam karte hain!")
        return

    if not await is_admin(message.chat, message.from_user.id):
        await message.reply_text("❌ Aapke paas is command ko use karne ke liye Admin permissions nahi hain!")
        return

    # Extract command cleanly even if username is attached
    command_raw = message.command[0].lower()
    command = command_raw.split("@")[0]
    
    target_user = await extract_user(client, message)

    if not target_user:
        await message.reply_text(f"❌ Kripya kisi user ko reply karein ya unka username/ID dalein.\nExample: `/{command} @username`")
        return

    if await is_admin(message.chat, target_user.id) and command not in ["approve", "disapprove"]:
        await message.reply_text("❌ Main kisi dusre Admin par action nahi le sakta!")
        return

    try:
        if command == "ban":
            await message.chat.ban_member(target_user.id)
            await message.reply_text(f"🚨 {target_user.mention} ko group se **Ban** kar diya gaya.")
        elif command == "unban":
            await message.chat.unban_member(target_user.id)
            await message.reply_text(f"✅ {target_user.mention} ko **Unban** kar diya gaya.")
        elif command == "mute":
            await message.chat.restrict_member(target_user.id, ChatPermissions(can_send_messages=False))
            await message.reply_text(f"🤐 {target_user.mention} ko **Mute** kar diya gaya.")
        elif command == "unmute":
            await message.chat.restrict_member(
                target_user.id, 
                ChatPermissions(
                    can_send_messages=True, can_send_media_messages=True,
                    can_send_other_messages=True, can_add_web_page_previews=True
                )
            )
            await message.reply_text(f"🔊 {target_user.mention} ko **Unmute** kar diya gaya.")
        elif command == "warn":
            await handle_member_violation(client, message, target_user, f"Manually Warned by Admin (@{message.from_user.username or message.from_user.id})")
        elif command == "diswarn":
            await db.reset_warns(message.chat.id, target_user.id)
            await message.reply_text(f"🔄 {target_user.mention} ki saari warnings reset/remove kar di gayi hain.")
        elif command == "approve":
            await db.approve_user(message.chat.id, target_user.id)
            await message.reply_text(f"🟢 {target_user.mention} ko whitelist kar diya gaya hai.")
        elif command == "disapprove":
            await db.disapprove_user(message.chat.id, target_user.id)
            await message.reply_text(f"🔴 {target_user.mention} ko whitelist se hata diya gaya hai.")
    except Exception as e:
        await message.reply_text(f"⚠️ Action Fail ho gaya: {e}")

# --- BROADCAST SYSTEM ---
@bot.on_message(filters.command(["broadcast", "bc", f"broadcast@{BOT_USERNAME}", f"bc@{BOT_USERNAME}"]) & filters.private)
async def advanced_broadcast(client, message: Message):
    if message.from_user.username != OWNER_USERNAME and message.from_user.id != Config.OWNER_ID:
        return
    target_msg = message.reply_to_message if message.reply_to_message else message
    if target_msg == message and len(message.command) < 2:
        await message.reply_text("❌ `/bc -all [text]` use karein.")
        return

    cmd_text = message.text or ""
    should_pin = "-pin" in cmd_text.lower()
    send_to_users = "-users" in cmd_text.lower()
    send_to_groups = "-groups" in cmd_text.lower()
    send_to_all = "-all" in cmd_text.lower() or (not send_to_users and not send_to_groups)

    status_msg = await message.reply_text("⚡ **ʙʀᴏᴀᴅᴄᴀsᴛ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ...**")
    targets = []
    try:
        if send_to_users or send_to_all:
            users = await db.get_served_users()
            targets.extend([{"id": u["user_id"]} for u in users])
        if send_to_groups or send_to_all:
            chats = await db.get_served_chats()
            targets.extend([{"id": c["chat_id"]} for c in chats])
    except Exception as e:
        await status_msg.edit_text(f"❌ Database error during broadcast: {e}")
        return

    unique_targets = {t["id"]: t for t in targets}.values()
    success, failed = 0, 0

    for target in unique_targets:
        try:
            if message.reply_to_message:
                sent_msg = await target_msg.copy(chat_id=target["id"])
            else:
                clean_text = cmd_text.replace("/broadcast", "").replace("/bc", "").replace("-pin", "").replace("-users", "").replace("-groups", "").replace("-all", "").strip()
                sent_msg = await client.send_message(chat_id=target["id"], text=clean_text)
            if should_pin and sent_msg:
                try: await sent_msg.pin()
                except: pass
            success += 1
            await asyncio.sleep(0.3)
        except:
            failed += 1

    await status_msg.edit_text(f"📊 **ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n✅ Success: {success}\n❌ Failed: {failed}")

# --- AUTOMATED ULTIMATE SECURITY WATCHER ENGINE ---
@bot.on_message(filters.group & ~filters.service, group=1)
async def security_watcher(client, message: Message):
    if not message.from_user: return
    
    user_id = message.from_user.id
    is_user_admin = await is_admin(message.chat, user_id)
    
    try: is_user_approved = await db.is_approved(message.chat.id, user_id)
    except: is_user_approved = False
    
    text_content = message.text or message.caption or ""
    has_link = bool(re.search(r"t\.me|http|www\.", text_content))

    # 1. ANTI LINK SYSTEM
    if has_link:
        if not (is_user_admin or is_user_approved):
            try: await message.delete()
            except: pass
            await handle_member_violation(client, message, message.from_user, "Anti Link Violation (Sent Forbidden Link)")
            return

    # 2. NSFW & DRUG CONTENT FILTER 
    is_nsfw_or_drug = any(word in text_content.lower() for word in NSFW_DRUG_KEYWORDS)
    if message.has_media_spoiler:
        is_nsfw_or_drug = True

    if is_nsfw_or_drug:
        if not (is_user_admin or is_user_approved):
            try: await message.delete()
            except: pass
            await handle_member_violation(client, message, message.from_user, "NSFW / Illegal Drug Content Violation")
            return

    # --- BELOW RESTRICTIONS ONLY FOR NON-ADMIN MEMBERS ---
    if is_user_admin or is_user_approved:
        return

    # 3. BIO LINK PROTECTION
    try:
        user_bio = (await client.get_users(user_id)).bio or ""
        if re.search(r"t\.me|http|www\.", user_bio):
            try: await message.delete()
            except: pass
            await handle_member_violation(client, message, message.from_user, "Bio Link Violation (Links inside Telegram Profile Bio)")
            return
    except: pass

    # 4. ANTI ABUSE PROTECTION
    for word in BAD_WORDS:
        if word in text_content.lower():
            try: await message.delete()
            except: pass
            await handle_member_violation(client, message, message.from_user, "Anti Abuse System (Used Profanity/Abusive Language)")
            return

    # 5. FORWARD CONTROL
    if message.forward_date or message.forward_from or message.forward_from_chat:
        try: await message.delete()
        except: pass
        await handle_member_violation(client, message, message.from_user, "Forward Control System (Forwards strictly Prohibited)")
        return

# --- EDIT SECURITY SYSTEM ---
@bot.on_edited_message(filters.group)
async def edit_security_engine(client, message: Message):
    if not message.from_user: return
    
    text_content = message.text or message.caption or ""
    has_link = bool(re.search(r"t\.me|http|www\.", text_content))
    
    if has_link:
        try: await message.delete()
        except: pass
        is_user_admin = await is_admin(message.chat, message.from_user.id)
        try: is_user_approved = await db.is_approved(message.chat.id, message.from_user.id)
        except: is_user_approved = False
        
        if not (is_user_admin or is_user_approved):
            await handle_member_violation(client, message, message.from_user, "Edit Security (Tried to bypass anti-link via message Editing)")

# --- WELCOME AND TRACKING COMMANDS ---
@bot.on_message(filters.command(["welcomeset", f"welcomeset@{BOT_USERNAME}"]) & filters.group)
async def set_welcome_msg(client, message: Message):
    if not await is_admin(message.chat, message.from_user.id): return
    photo_msg = message if message.photo else (message.reply_to_message if message.reply_to_message and message.reply_to_message.photo else None)
    if not photo_msg:
        await message.reply_text("❌ Kisi photo ke caption me `/welcomeset [text]` likhein!")
        return
    fid = photo_msg.photo.file_id
    full_text = message.text or message.caption or ""
    text_w = full_text.replace("/welcomeset", "").strip()
    cap = text_w
    btn_raw = ""
    if "[" in text_w and "]" in text_w:
        start_idx = text_w.find("[")
        cap = text_w[:start_idx].strip()
        btn_raw = text_w[start_idx:].strip()
    await db.set_welcome(message.chat.id, fid, cap, btn_raw if btn_raw else None)
    await message.reply_text("✅ Custom Welcome with Image Saved!")

@bot.on_message(filters.new_chat_members & filters.group)
async def welcome_action(client, message: Message):
    try: await db.add_served_chat(message.chat.id)
    except: pass
    w_data = await db.get_welcome(message.chat.id)
    if not w_data: return
    cnt = await client.get_chat_members_count(message.chat.id)
    for m in message.new_chat_members:
        un = f"@{m.username}" if m.username else "No Username"
        cap = w_data["caption"].replace("{mention}", m.mention).replace("{name}", m.first_name).replace("{id}", str(m.id)).replace("{username}", un).replace("{title}", message.chat.title).replace("{count}", str(cnt))
        btns = parse_buttons(w_data.get("buttons"))
        markup = InlineKeyboardMarkup(btns) if btns else None
        try: await client.send_photo(chat_id=message.chat.id, photo=w_data["file_id"], caption=cap, reply_markup=markup)
        except: pass

# --- MODERN ASYNC LOOP EXECUTION ENGINE ---
async def main():
    await start_server()
    print("🤖 STARTING BOT CLIENT SESSION...")
    try:
        await bot.start()
        print("✅ GUARDIAN PRO SECURITY ENGINE STARTED SUCCESSFULLY AND ALIVE!")
    except Exception as e:
        print(f"❌ BOT START CRASHED: {e}")
    
    # Render loop fix: secure wait without crashing
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot deployment stopped safely.")
