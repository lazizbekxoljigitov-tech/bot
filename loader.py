"""
loader.py - Initializes core bot components.
Creates Bot instance, Dispatcher, and MemoryStorage.
"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN

# ---- FSM storage (in-memory) ----
storage = MemoryStorage()

# ---- Bot instance with HTML parse mode ----
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

# ---- Dispatcher ----
dp = Dispatcher(storage=storage)
