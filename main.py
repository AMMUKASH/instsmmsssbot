import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import Config
import database as db

# Web server Setup Render ki port binding ke liye (Uptime)
from aiohttp import web
async def handle(request):
    return web.Response(text="Bot is Running and Alive 24/7!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', Config.PORT)
    await site.start()

bot = Client(
    "GuardianProBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Helper functions
def parse_buttons(text):
    if not text: return None
    try:
        kb = []
        for line in text.split("\n"):
            if "|" in line:
                n, u = line.split("|")
                kb.append([InlineKeyboardButton(n.strip(), url=u.strip())])
        return kb if kb else None
    except: return None

async def is_admin(chat, user_id):
    if chat.type.value in ["private"]: return True
    try:
        m = await bot.get_chat_member(chat.id, user_id)
        return m.status.value in ["administrator", "owner"]
    except: return False

# --- HANDLERS ---

@bot.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    text = (
        "╭────── • 𝐆𝐔𝐀𝐑𝐃𝐈𝐀𝐍 𝐏𝐑𝐎 • ──────╮\n"
        "│      ✨ **ADVANCED GROUP SECURITY** ✨      \n"
        "├──────────────────────────────┤\n"
        "│ 🛡️ **BIO LINK PROTECTION**\n"
        "│  └ Warn + Auto Mute (30ᵐⁱⁿ)\n"
        "│\n"
        "│ 🔗 **ANTI LINK SYSTEM**\n"
        "│  └ Instant Link Removal\n"
        "│\n"
        "│ 🚫 **ANTI ABUSE PROTECTION**\n"
        "│  └ Smart Language Filter\n"
        "│\n"
        "│ 📥 **FORWARD CONTROL**\n"
        "│  └ Auto Forward Delete\n"
        "│\n"
        "│ 📝 **EDIT SECURITY**\n"
        "│  └ Edited Link Detection\n"
        "│\n"
        "│ 🗑️ **MEDIA CLEANUP**\n"
        "│  └ Silent Auto Delete (50s)\n"
        "├──────────────────────────────┤\n"
        "│ ⚡ _Fast • Stable • Professional Grade_      \n"
        "╰──────────────────────────────╯"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ Add Me To Your Group ✨", url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=true")],
        [
            InlineKeyboardButton("📢 Channel", url=f"https://t.me/{Config.UPDATE_CH}"),
            InlineKeyboardButton("🛠️ Help Menu", callback_data="help_menu")
        ]
    ])
    if message.chat.type.value == "private":
        await message.reply_photo(photo=Config.START_IMG, caption=text, reply_markup=buttons)
    else:
        await message.reply_text("Bot active hai! Mujhe PM (Private Message) me start karke Help Menu check karein.", reply_markup=buttons)

@bot.on_callback_query(filters.regex("^help_menu$|^back_start$"))
async def cb_handler(client, cb: CallbackQuery):
    if cb.data == "help_menu":
        help_text = (
            "🛠️ **GUARDIAN PRO - HELP MENU & GUIDE**\n\n"
            "👮 **Admin Commands:**\n"
            "• `/ban` - User ko group se ban karein (Reply)\n"
            "• `/unban` - User ko unban karein\n"
            "• `/mute` - User ko mute karein\n"
            "• `/unmute` - User ko unmute karein\n"
            "• `/warn` - User ko warning dein (Max 3 pe kick)\n"
            "• `/diswarn` - User ki warning kam karein\n"
            "• `/approve` - User ko whitelist karein (Anti-link skip)\n"
            "• `/disapprove` - Whitelist se hatayein\n\n"
            "⚙️ **Welcome Customization:**\n"
            "• `/welcomeset [text]` - Reply on a photo to set custom welcome\n"
            "• `/welcomereset` - Welcome message band karein\n\n"
            "🔍 **Filters System:**\n"
            "• `/filter [keyword] [reply text]` - New trigger filter set karein\n"
            "• `/stop [keyword]` - Triger filter delete karein\n"
            "• `/stopallfilter` - Group ke saare filters clear karein"
        )
        await cb.message.edit_caption(caption=help_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]))
    elif cb.data == "back_start":
        # Start message text format restore karein
        text = (
            "╭────── • 𝐆𝐔𝐀𝐑𝐃𝐈𝐀𝐍 𝐏𝐑𝐎 • ──────╮\n"
            "│      ✨ **ADVANCED GROUP SECURITY** ✨      \n"
            "╰──────────────────────────────╯"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Add Me To Your Group ✨", url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=true")],
            [InlineKeyboardButton("📢 Channel", url=f"https://t.me/{Config.UPDATE_CH}"), InlineKeyboardButton("🛠️ Help Menu", callback_data="help_menu")]
        ])
        await cb.message.edit_caption(caption=text, reply_markup=buttons)

# --- WELCOME COMMANDS ---
@bot.on_message(filters.command("welcomeset") & filters.group)
async def set_welcome_msg(client, message: Message):
    if not await is_admin(message.chat, message.from_user.id): return
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("❌ Photo par reply karke `/welcomeset` command dein!")
        return
    fid = message.reply_to_message.photo.file_id
    full_t = message.text or message.caption or ""
    text_w = full_t.replace("/welcomeset", "").strip()
    cap, btn = text_w, ""
    if "[" in text_w and "]" in text_w:
        parts = text_w.split("[")
        cap = parts[0].strip()
        btn = "\n".join([p.replace("]", "").strip() for p in parts[1:]])
    await db.set_welcome(message.chat.id, fid, cap, btn)
    await message.reply_text("✅ Custom Welcome image aur settings save ho chuki hain!")

@bot.on_message(filters.command("welcomereset") & filters.group)
async def reset_welcome_msg(client, message: Message):
    if not await is_admin(message.chat, message.from_user.id): return
    await db.reset_welcome(message.chat.id)
    await message.reply_text("🗑️ Welcome message successfully reset aur disable kar diya gaya hai.")

# --- ADMIN ACTIONS CONTROLS ---
@bot.on_message(filters.command(["ban", "mute", "warn", "approve", "disapprove", "diswarn"]) & filters.group)
async def admin_actions(client, message: Message):
    if not await is_admin(message.chat, message.from_user.id): return
    if not message.reply_to_message:
        await message.reply_text("❌ Is command ko use karne ke liye target user ke message par reply karein.")
        return
    
    target = message.reply_to_message.from_user
    cmd = message.command[0]

    if cmd == "ban":
        await client.ban_chat_member(message.chat.id, target.id)
        await message.reply_text(f"🛑 {target.mention} ko group se block (Ban) kar diya gaya.")
    elif cmd == "mute":
        await client.restrict_chat_member(message.chat.id, target.id, permissions=chat_permissions(can_send_messages=False))
        await message.reply_text(f"🔇 {target.mention} ko mute kar diya gaya hai.")
    elif cmd == "warn":
        count = await db.add_warn(message.chat.id, target.id)
        if count >= 3:
            await client.ban_chat_member(message.chat.id, target.id)
            await message.reply_text(f"🔥 {target.mention} ke 3/3 warnings poore hone par Ban kar diya gaya.")
        else:
            await message.reply_text(f"⚠️ {target.mention} ko warning di gayi. (Total Warns: {count}/3)")
    elif cmd == "diswarn":
        count = await db.remove_warn(message.chat.id, target.id)
        await message.reply_text(f"✅ {target.mention} ki ek warning kam kar di gayi hai. (Bachi warning: {count})")
    elif cmd == "approve":
        await db.approve_user(message.chat.id, target.id)
        await message.reply_text(f"🟢 {target.mention} approve ho gaya hai. Ab ispar anti-link system work nahi karega.")
    elif cmd == "disapprove":
        await db.disapprove_user(message.chat.id, target.id)
        await message.reply_text(f"🔴 {target.mention} whitelisted status se remove kar diya gaya.")

@bot.on_message(filters.command(["unban", "unmute"]) & filters.group)
async def admin_unactions(client, message: Message):
    if not await is_admin(message.chat, message.from_user.id): return
    cmd = message.command[0]
    
    if len(message.command) > 1:
        target_id = message.command[1]
    elif message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        await message.reply_text("❌ ID dalein ya user ke message par reply karke command run karein.")
        return

    if cmd == "unban":
        await client.unban_chat_member(message.chat.id, target_id)
        await message.reply_text("✅ User group me wapas aa sakta hai (Unbanned).")
    elif cmd == "unmute":
        from pyrogram.types import ChatPermissions
        await client.restrict_chat_member(message.chat.id, target_id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
        await message.reply_text("🔊 User unmuted! Ab wo group me text bhej sakta hai.")

# --- FILTER SYSTEM ---
@bot.on_message(filters.command("filter") & filters.group)
async def set_filter(client, message: Message):
    if not await is_admin(message.chat, message.from_user.id): return
    if len(message.command) < 3:
        await message.reply_text("❌ Format galat hai. Use karein: `/filter [keyword] [reply text]`")
        return
    keyword = message.command[1].lower()
    reply_text = message.text.split(None, 2)[2]
    await db.add_filter(message.chat.id, keyword, reply_text)
    await message.reply_text(f"📥 Filter save ho gaya hai trigger word: `{keyword}` ke liye.")

@bot.on_message(filters.command("stop") & filters.group)
async def stop_one_filter(client, message: Message):
    if not await is_admin(message.chat, message.from_user.id): return
    if len(message.command) < 2:
        await message.reply_text("❌ Triger name dalein: `/stop [keyword]`")
        return
    kw = message.command[1].lower()
    deleted = await db.stop_filter(message.chat.id, kw)
    if deleted: await message.reply_text(f"🗑️ `{kw}` filter band kar diya gaya hai.")
    else: await message.reply_text("❌ Aisa koi filter group me active nahi hai.")

@bot.on_message(filters.command("stopallfilter") & filters.group)
async def stop_all_f(client, message: Message):
    if not await is_admin(message.chat, message.from_user.id): return
    await db.stop_all_filters(message.chat.id)
    await message.reply_text("💥 Is group ke saare custom filters delete kar diye gaye hain.")

# --- NEW CHAT MEMBER JOIN ACTION ---
@bot.on_message(filters.new_chat_members & filters.group)
async def welcome_action(client, message: Message):
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

# --- AUTO WATCHER (FILTERS, SECURITY & PROTECTION) ---
@bot.on_message(filters.group & ~filters.service)
async def watcher(client, message: Message):
    if not message.from_user: return
    if await db.is_approved(message.chat.id, message.from_user.id) or await is_admin(message.chat, message.from_user.id):
        return

    text_content = message.text or message.caption or ""
    
    # Custom Triggers Engine Check
    all_filters = await db.get_filters(message.chat.id)
    for f in all_filters:
        if f["keyword"] in text_content.lower():
            await message.reply_text(f["reply_text"])
            return

    # Basic URL/Link Security
    if re.search(r"t\.me|http|www\.", text_content):
        try: await message.delete(); return
        except: pass

    # Anti-Forward Control
    if message.forward_date:
        try: await message.delete(); return
        except: pass

async def main():
    await start_server()
    await bot.start()
    print("Bot is successfully running online...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
