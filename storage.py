import os
from pymongo import MongoClient
from telegram.constants import ChatType

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB", "telegram_tagger")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

tags_col = db.tags
filters_col = db.filters
users_col = db.users
groups_col = db.groups

# ---------- TAG SENTENCES ----------
def get_tags():
    doc = tags_col.find_one({"_id": "tags"})
    return doc["lines"] if doc and "lines" in doc else []

def add_tag(text):
    tags_col.update_one(
        {"_id": "tags"},
        {"$push": {"lines": text}},
        upsert=True
    )

def delete_tag(index):
    tags = get_tags()
    if index < 0 or index >= len(tags):
        return None
    removed = tags.pop(index)
    tags_col.update_one(
        {"_id": "tags"},
        {"$set": {"lines": tags}},
        upsert=True
    )
    return removed

def tag_count():
    return len(get_tags())

# ---------- FILTERS ----------
def add_filter(chat_id, trigger, payload):
    filters_col.update_one(
        {"chat_id": chat_id},
        {"$set": {f"filters.{trigger}": payload}},
        upsert=True
    )

def delete_filter(chat_id, trigger):
    filters_col.update_one(
        {"chat_id": chat_id},
        {"$unset": {f"filters.{trigger}": ""}}
    )

def get_filters(chat_id):
    doc = filters_col.find_one({"chat_id": chat_id})
    return doc.get("filters", {}) if doc else {}

# ---------- USERS / GROUPS ----------
async def collect_chat(update, _):
    if update.effective_user:
        users_col.update_one(
            {"user_id": update.effective_user.id},
            {"$set": {"user_id": update.effective_user.id}},
            upsert=True
        )

    if update.effective_chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        groups_col.update_one(
            {"chat_id": update.effective_chat.id},
            {"$set": {"chat_id": update.effective_chat.id}},
            upsert=True
        )
