import time
from telegram.ext import CommandHandler, MessageHandler, filters
from storage import add_filter, delete_filter, get_filters

COOLDOWN = 3
LAST = {}

async def is_admin(chat, uid):
    admins = await chat.get_administrators()
    return uid in [a.user.id for a in admins]

async def addfilter(update, context):
    if not await is_admin(update.effective_chat, update.effective_user.id):
        return await update.message.reply_text("Admins only")

    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("Reply: /addfilter trigger")

    r = update.message.reply_to_message
    payload = {"type":"text","text":r.text or r.caption}

    if r.photo: payload={"type":"photo","id":r.photo[-1].file_id}
    elif r.video: payload={"type":"video","id":r.video.file_id}
    elif r.sticker: payload={"type":"sticker","id":r.sticker.file_id}
    elif r.animation: payload={"type":"animation","id":r.animation.file_id}
    elif r.voice: payload={"type":"voice","id":r.voice.file_id}
    elif r.document: payload={"type":"document","id":r.document.file_id}

    add_filter(update.effective_chat.id, context.args[0].lower(), payload)
    await update.message.reply_text("✅ Filter saved")

async def delfilter(update, context):
    if not await is_admin(update.effective_chat, update.effective_user.id):
        return
    delete_filter(update.effective_chat.id, context.args[0].lower())
    await update.message.reply_text("🗑 Filter deleted")

async def watch(update, context):
    msg = update.message
    if not msg or msg.from_user.is_bot:
        return

    text = (msg.text or msg.caption or "").lower()
    cid = update.effective_chat.id

    for k,v in get_filters(cid).items():
        if k in text:
            key=(cid,msg.from_user.id)
            now=time.time()
            if key in LAST and now-LAST[key]<COOLDOWN:
                return
            LAST[key]=now

            t=v["type"]
            if t=="text": await msg.reply_text(v["text"])
            elif t=="photo": await msg.reply_photo(v["id"])
            elif t=="video": await msg.reply_video(v["id"])
            elif t=="sticker": await msg.reply_sticker(v["id"])
            elif t=="animation": await msg.reply_animation(v["id"])
            elif t=="voice": await msg.reply_voice(v["id"])
            elif t=="document": await msg.reply_document(v["id"])
            break

def setup_filters(app):
    app.add_handler(CommandHandler("addfilter", addfilter))
    app.add_handler(CommandHandler("delfilter", delfilter))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, watch))
