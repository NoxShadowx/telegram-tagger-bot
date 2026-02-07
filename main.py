import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from tag import tag_single, tagcancel, addtag, tagcount
from filters import addfilter, delfilter, listfilters, watch_filters
from broadcast import broadcast, broadcast_btn
from db import users_col, groups_col

async def collect(update, context):
    if update.effective_user:
        await users_col.update_one({"id": update.effective_user.id}, {"$set": {"id": update.effective_user.id}}, upsert=True)
    if update.effective_chat.type in ("group", "supergroup"):
        await groups_col.update_one({"id": update.effective_chat.id}, {"$set": {"id": update.effective_chat.id}}, upsert=True)

async def start(update, context):
    await update.message.reply_text(
        "🤖 Advanced Tagger Bot (MongoDB)\n\n"
        "/tag @user\n"
        "/tagcancel\n\n"
        "Filters:\n"
        "/addfilter (admin)\n"
        "/delfilter (admin)\n"
        "/filters\n\n"
        "Owner:\n"
        "/addtag\n"
        "/tagcount\n"
        "/broadcast\n"
    )

def main():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tag", tag_single))
    app.add_handler(CommandHandler("tagcancel", tagcancel))
    app.add_handler(CommandHandler("addtag", addtag))
    app.add_handler(CommandHandler("tagcount", tagcount))

    app.add_handler(CommandHandler("addfilter", addfilter))
    app.add_handler(CommandHandler("delfilter", delfilter))
    app.add_handler(CommandHandler("filters", listfilters))

    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(broadcast_btn))

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, watch_filters))
    app.add_handler(MessageHandler(filters.ALL, collect))

    app.run_webhook("0.0.0.0", int(os.getenv("PORT")), webhook_url=os.getenv("WEBHOOK_URL"))

if __name__ == "__main__":
    main()
