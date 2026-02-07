import time, random, asyncio
from telegram.ext import CommandHandler
from storage import get_tags, add_tag, delete_tag, tag_count

OWNER_ID = 8455806295
MAX_SINGLE_TAG = 50
ANTI_SPAM = 8

TAG_TASKS = {}
LAST_TIME = {}

DEFAULT_TAGS = [
    "{user} ɪᴅʜᴀʀ ᴀᴀᴏ ᴛʜᴏᴅᴀ sᴀ ʙᴀᴀᴛ ᴋᴀʀɴɪ ʜᴀɪ 👀",
    "{user} ᴋᴀʜᴀ ʜᴏ ᴀᴀᴊ ᴅɪᴋʜᴀɪ ɴᴀʜɪ ʀᴀʜᴇ 🤨",
    "{user} ᴏɴʟɪɴᴇ ᴀᴀ ᴊᴀᴏ ɢʀᴏᴜᴘ ᴛᴜᴍʜᴇ ʏᴀᴀᴅ ᴋᴀʀ ʀᴀʜᴀ 😜",
]

# ensure defaults exist
if not get_tags():
    for t in DEFAULT_TAGS:
        add_tag(t)

def stop(chat_id):
    task = TAG_TASKS.pop(chat_id, None)
    if task:
        task.cancel()

def allowed(chat_id):
    now = time.time()
    if chat_id in LAST_TIME and now - LAST_TIME[chat_id] < ANTI_SPAM:
        return False
    LAST_TIME[chat_id] = now
    return True

# ---------- SINGLE USER TAG ----------
async def tag(update, context):
    chat = update.effective_chat
    msg = update.message

    if not allowed(chat.id):
        return await msg.reply_text("⏳ Slow down")

    ent = next((e for e in msg.entities or [] if e.type in ("mention","text_mention")), None)
    if not ent:
        return await msg.reply_text("Usage: /tag @user [text]")

    user = ent.user if ent.type == "text_mention" else await context.bot.get_chat(
        msg.text[ent.offset: ent.offset+ent.length]
    )

    stop(chat.id)

    text = msg.text.replace(msg.text.split()[0], "").strip()
    tags = get_tags()
    if not text:
        text = random.choice(tags)
    if "{user}" not in text:
        text = f"{user.mention_html()} {text}"

    async def run():
        for _ in range(MAX_SINGLE_TAG):
            await msg.reply_html(text)
            await asyncio.sleep(2)

    TAG_TASKS[chat.id] = asyncio.create_task(run())
    await msg.reply_text("✅ Tagging started (auto-stops at 50)")

# ---------- CANCEL ----------
async def tagcancel(update, _):
    stop(update.effective_chat.id)
    await update.message.reply_text("❌ Tagging cancelled")

# ---------- OWNER TAG MANAGEMENT ----------
async def addtag_cmd(update, context):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Owner only")

    text = " ".join(context.args)
    if not text or "{user}" not in text:
        return await update.message.reply_text("Usage: /addtag {user} sentence")

    add_tag(text)
    await update.message.reply_text(f"✅ Tag added | Total: {tag_count()}")

async def deltag_cmd(update, context):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("Usage: /deltag <number>")

    removed = delete_tag(int(context.args[0]) - 1)
    if not removed:
        return await update.message.reply_text("Invalid index")

    await update.message.reply_text(f"🗑 Removed:\n{removed}")

async def tagcount_cmd(update, _):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text(f"📊 Total tags: {tag_count()}")

def setup_tag(app):
    app.add_handler(CommandHandler("tag", tag))
    app.add_handler(CommandHandler("tagcancel", tagcancel))
    app.add_handler(CommandHandler("addtag", addtag_cmd))
    app.add_handler(CommandHandler("deltag", deltag_cmd))
    app.add_handler(CommandHandler("tagcount", tagcount_cmd))
