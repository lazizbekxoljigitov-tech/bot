"""
handlers/admin/stats.py - Statistika handleri (admin).
Bot statistikalarini ko'rsatish.
"""

import logging

from aiogram import Router, F
from aiogram.types import Message
from models.admin import AdminModel
from services.stats_service import StatsService

logger = logging.getLogger(__name__)
router = Router(name="admin_stats")


@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message) -> None:
    """Admin uchun statistika ko'rsatish."""
    if not await AdminModel.is_admin(message.from_user.id):
        return
    text = await StatsService.get_stats_text()
    await message.answer(text)
