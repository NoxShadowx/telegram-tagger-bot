import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set")

client = AsyncIOMotorClient(MONGO_URI)
db = client["telegram_tagger_bot"]

tags_col = db.tags           # global tag sentences
filters_col = db.filters     # group-wise filters
users_col = db.users
groups_col = db.groups
