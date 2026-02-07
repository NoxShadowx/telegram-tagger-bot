import os
from telegram.ext import Application, MessageHandler, filters
from storage import collect_chat
from tag import setup_tag
from filters import setup_filters
from broadcast import setup_broadcast

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    setup_tag(app)
    setup_filters(app)
    setup_broadcast(app)

    app.add_handler(MessageHandler(filters.ALL, collect_chat))

    app.run_webhook("0.0.0.0", PORT, webhook_url=WEBHOOK_URL)

if __name__ == "__main__":
    main()
