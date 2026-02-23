"""
handlers/admin/stats.py - Statistika handleri (admin).
Bot statistikalarini ko'rsatish.
"""

import logging

from aiogram import Router, F
from aiogram.types import Message
from models.admin import AdminModel
from filters.admin import is_admin
from services.stats_service import StatsService


logger = logging.getLogger(__name__)
router = Router(name="admin_stats")


@router.message(F.text == "📊 Statistika", is_admin)
async def show_stats(message: Message) -> None:
    """Admin uchun statistika ko'rsatish."""

    text = await StatsService.get_stats_text()
    await message.answer(text)
