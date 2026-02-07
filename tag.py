import os
import time
import random
import asyncio
from telegram.constants import ChatType
from db import tags_col


ANTI_SPAM_SECONDS = int(os.getenv("ANTI_SPAM_SECONDS", 8))
MAX_SINGLE_TAG = int(os.getenv("MAX_SINGLE_TAG", 50))

TAG_TASKS = {}
LAST_CMD = {}

def anti_spam(chat_id):
    now = time.time()
    if chat_id in LAST_CMD and now - LAST_CMD[chat_id] < ANTI_SPAM_SECONDS:
        return False
    LAST_CMD[chat_id] = now
    return True

def stop_tag(chat_id):
    task = TAG_TASKS.pop(chat_id, None)
    if task:
        task.cancel()

async def get_random_tag():
    docs = await tags_col.find().to_list(1000)
    return random.choice(docs)["text"]

async def tag_single(update, context):
    chat = update.effective_chat
    msg = update.message

    if not anti_spam(chat.id):
        return await msg.reply_text("⏳ Slow down")

    ent = next((e for e in (msg.entities or []) if e.type in ("mention", "text_mention")), None)
    if not ent:
        return await msg.reply_text("Usage: /tag @user [text]")

    user = ent.user if ent.type == "text_mention" else await context.bot.get_chat(
        msg.text[ent.offset: ent.offset + ent.length]
    )

    stop_tag(chat.id)

    text = msg.text.replace(msg.text.split()[0], "").strip()
    if not text:
        text = await get_random_tag()

    if "{user}" not in text:
        text = f"{user.mention_html()} {text}"

    async def run():
        for _ in range(MAX_SINGLE_TAG):
            await msg.reply_html(text)
            await asyncio.sleep(2)

    TAG_TASKS[chat.id] = asyncio.create_task(run())
    await msg.reply_text("✅ Tagging started (auto-stops at 50)")

async def tagcancel(update, context):
    stop_tag(update.effective_chat.id)
    await update.message.reply_text("❌ Tagging cancelled")

async def addtag(update, context):
    if update.effective_user.id != int(os.getenv("OWNER_USER_ID")):
        return

    text = " ".join(context.args)
    if not text or "{user}" not in text:
        return await update.message.reply_text("Usage: /addtag {user} sentence")

    await tags_col.insert_one({"text": text})
    await update.message.reply_text("✅ Tag sentence added")

async def tagcount(update, context):
    if update.effective_user.id != int(os.getenv("OWNER_USER_ID")):
        return
    count = await tags_col.count_documents({})
    await update.message.reply_text(f"📊 Total tag sentences: {count}")
