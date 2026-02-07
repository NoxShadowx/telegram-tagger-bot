import os
import time
from telegram.constants import ChatType
from db import filters_col


FILTER_COOLDOWN = int(os.getenv("FILTER_COOLDOWN", 3))
COOLDOWN = {}

async def is_admin(update):
    chat = update.effective_chat
    if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return False
    admins = await chat.get_administrators()
    return update.effective_user.id in [a.user.id for a in admins]

async def addfilter(update, context):
    if not await is_admin(update):
        return await update.message.reply_text("❌ Admins only")

    msg = update.message
    if not msg.reply_to_message or not context.args:
        return await msg.reply_text("Reply: /addfilter trigger")

    trigger = context.args[0].lower()
    r = msg.reply_to_message

    payload = {"type": "text", "text": r.text or r.caption}
    if r.photo:
        payload = {"type": "photo", "file_id": r.photo[-1].file_id}
    elif r.video:
        payload = {"type": "video", "file_id": r.video.file_id}
    elif r.sticker:
        payload = {"type": "sticker", "file_id": r.sticker.file_id}
    elif r.animation:
        payload = {"type": "animation", "file_id": r.animation.file_id}
    elif r.voice:
        payload = {"type": "voice", "file_id": r.voice.file_id}
    elif r.document:
        payload = {"type": "document", "file_id": r.document.file_id}

    await filters_col.update_one(
        {"chat_id": update.effective_chat.id, "trigger": trigger},
        {"$set": {"payload": payload}},
        upsert=True
    )

    await msg.reply_text(f"✅ Filter `{trigger}` saved")

async def delfilter(update, context):
    if not await is_admin(update):
        return
    if not context.args:
        return
    await filters_col.delete_one({
        "chat_id": update.effective_chat.id,
        "trigger": context.args[0].lower()
    })
    await update.message.reply_text("🗑 Filter deleted")

async def listfilters(update, context):
    cur = filters_col.find({"chat_id": update.effective_chat.id})
    triggers = [f["trigger"] async for f in cur]
    if not triggers:
        return await update.message.reply_text("No filters")
    await update.message.reply_text("\n".join(triggers))

async def watch_filters(update, context):
    msg = update.message
    if not msg or msg.from_user.is_bot:
        return

    key = (msg.chat_id, msg.from_user.id)
    now = time.time()
    if key in COOLDOWN and now - COOLDOWN[key] < FILTER_COOLDOWN:
        return

    text = (msg.text or msg.caption or "").lower()
    if not text:
        return

    async for f in filters_col.find({"chat_id": msg.chat_id}):
        if f["trigger"] in text:
            COOLDOWN[key] = now
            p = f["payload"]
            t = p["type"]

            if t == "text":
                await msg.reply_text(p["text"])
            elif t == "photo":
                await msg.reply_photo(p["file_id"])
            elif t == "video":
                await msg.reply_video(p["file_id"])
            elif t == "sticker":
                await msg.reply_sticker(p["file_id"])
            elif t == "animation":
                await msg.reply_animation(p["file_id"])
            elif t == "voice":
                await msg.reply_voice(p["file_id"])
            elif t == "document":
                await msg.reply_document(p["file_id"])
            break
