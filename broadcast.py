from telegram.ext import CommandHandler
from storage import users_col, groups_col

OWNER_ID = 8455806295

async def broadcast(update, context):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Owner only")

    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to a message")

    msg = update.message.reply_to_message
    sent = 0

    for u in users_col.find():
        try:
            await msg.copy(u["user_id"])
            sent += 1
        except:
            pass

    for g in groups_col.find():
        try:
            await msg.copy(g["chat_id"])
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {sent}")

def setup_broadcast(app):
    app.add_handler(CommandHandler("broadcast", broadcast))
