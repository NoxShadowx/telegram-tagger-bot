import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


OWNER_ID = int(os.getenv("OWNER_USER_ID"))
CTX = {}

async def broadcast(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to a message")

    CTX[OWNER_ID] = update.message.reply_to_message

    kb = [
        [InlineKeyboardButton("👤 Users", callback_data="users")],
        [InlineKeyboardButton("👥 Groups", callback_data="groups")],
        [InlineKeyboardButton("🌍 All", callback_data="all")]
    ]

    await update.message.reply_text("Choose target:", reply_markup=InlineKeyboardMarkup(kb))

async def broadcast_btn(update, context):
    q = update.callback_query
    await q.answer()

    if q.from_user.id != OWNER_ID:
        return

    msg = CTX.get(OWNER_ID)
    if not msg:
        return await q.edit_message_text("Expired")

    if q.data == "users":
        ids = [u["id"] async for u in users_col.find()]
    elif q.data == "groups":
        ids = [g["id"] async for g in groups_col.find()]
    else:
        ids = [u["id"] async for u in users_col.find()] + \
              [g["id"] async for g in groups_col.find()]

    sent = 0
    for cid in ids:
        try:
            await msg.copy(cid)
            sent += 1
        except:
            pass

    await q.edit_message_text(f"✅ Broadcast sent to {sent}")
