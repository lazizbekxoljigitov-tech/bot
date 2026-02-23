"""
handlers/admin/tools.py - Administrative utility handlers.
Includes database health checks and system info.
"""

import logging
import os
from aiogram import Router, F
from aiogram.types import Message
from database import Database
from config import DB_PATH, LOG_FILE
from models.admin import AdminModel

logger = logging.getLogger(__name__)
router = Router(name="admin_tools")

async def is_admin(message: Message) -> bool:
    return await AdminModel.is_admin(message.from_user.id)

@router.message(F.text == "🛠 Boshqaruv", is_admin)
async def admin_tools_menu(message: Message):
    """Admin boshqaruv menyusi."""
    await message.answer(
        "🛠 <b>Boshqaruv va Diagnostika</b>\n\n"
        "Tizim holatini tekshirish uchun quyidagi buyruqdan foydalaning:\n"
        "/check_db - Ma'lumotlar bazasi holati\n"
        "/sys_info - Tizim ma'lumotlari"
    )

@router.message(F.command == "check_db", is_admin)
async def check_database(message: Message):
    """DB holatini tekshirish."""
    try:
        db = await Database.connect()
        # Integrity check
        cursor = await db.execute("PRAGMA integrity_check")
        row = await cursor.fetchone()
        integrity = row[0] if row else "Unknown"
        
        db_size = os.path.getsize(DB_PATH) / 1024 # KB
        
        await message.answer(
            "✅ <b>Ma'lumotlar bazasi:</b>\n\n"
            f"▸ Holat: Ishlamoqda\n"
            f"▸ Integrity: <code>{integrity}</code>\n"
            f"▸ Fayl: <code>{DB_PATH}</code>\n"
            f"▸ Hajm: {db_size:.2f} KB"
        )
    except Exception as e:
        await message.answer(f"❌ <b>DB Xatolik:</b>\n<code>{e}</code>")

@router.message(F.command == "sys_info", is_admin)
async def system_info(message: Message):
    """Tizim ma'lumotlari."""
    try:
        log_size = os.path.getsize(LOG_FILE) / 1024 if os.path.exists(LOG_FILE) else 0
        await message.answer(
            "💻 <b>Tizim ma'lumotlari:</b>\n\n"
            f"▸ OS: {os.name}\n"
            f"▸ Log fayl: <code>{LOG_FILE}</code>\n"
            f"▸ Log hajm: {log_size:.2f} KB"
        )
    except Exception as e:
        await message.answer(f"❌ <b>Xatolik:</b>\n<code>{e}</code>")
