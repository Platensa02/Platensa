import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
DATABASE_URL = os.environ.get("DATABASE_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL topilmadi")