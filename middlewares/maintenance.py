import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, Update

from models.settings import SettingsModel
from models.admin import AdminModel
from utils.images import IMAGES

logger = logging.getLogger(__name__)


class MaintenanceMiddleware(BaseMiddleware):
    """Botda texnik ishlar ketayotganini tekshirish."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        # Faqat xabarlar (Message) uchun tekshiramiz
        if not isinstance(event, Message):
            return await handler(event, data)

        # Admin ekanligini tekshirish
        is_admin = await AdminModel.is_admin(event.from_user.id)
        if is_admin:
            return await handler(event, data)

        # Texnik ishlar rejimini tekshirish
        maintenance = await SettingsModel.get("maintenance_mode", "OFF")
        if maintenance == "ON":
            caption = (
                "🛠 <b>TEXNIK ISHLAR</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ Botda hozirda texnik sozlash ishlari olib borilmoqda.\n\n"
                "⏳ <i>Iltimos, birozdan so'ng qayta urinib ko'ring. Noqulayliklar uchun uzr so'raymiz!</i>"
            )
            try:
                await event.answer_photo(
                    photo=IMAGES["MAINTENANCE"],
                    caption=caption
                )
            except Exception as e:
                logger.error(f"Error sending maintenance photo: {e}")
                await event.answer(caption)
            return

        return await handler(event, data)
