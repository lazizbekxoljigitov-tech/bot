"""
config.py - Bot configuration module.
Loads environment variables and defines global settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---- Load .env file ----
load_dotenv()

# ---- Base directory ----
BASE_DIR = Path(__file__).resolve().parent

# ---- Bot token (required) ----
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the environment variables.")

# ---- Admin IDs (comma-separated in .env) ----
_admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = [
    int(uid.strip()) for uid in _admin_ids_raw.split(",") if uid.strip().isdigit()
]

# ---- Database path ----
DB_PATH: str = str(BASE_DIR / "data" / "bot.db")

# ---- Logging ----
LOG_DIR: str = str(BASE_DIR / "logs")
LOG_FILE: str = str(Path(LOG_DIR) / "bot.log")

# ---- Pagination ----
EPISODES_PER_PAGE: int = 5
SEARCH_RESULTS_PER_PAGE: int = 5
SHORTS_PER_PAGE: int = 1

# ---- VIP payment card number (admin sets this) ----
VIP_CARD_NUMBER: str = os.getenv("VIP_CARD_NUMBER", "8600 0000 0000 0000")
