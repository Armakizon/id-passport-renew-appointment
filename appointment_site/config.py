import os

DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///local.db")
RESET_TOKEN = os.environ.get("RESET_TOKEN", "devtoken")
TIMEZONE = "Asia/Jerusalem"
