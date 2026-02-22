"""
middlewares/subscription.py - Majburiy obuna tekshirish middleware.
Foydalanuvchi barcha kanallarga obuna bo'lganini tekshiradi.
"""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus

from models.channel import ChannelModel
from keyboards.inline import subscription_keyboard

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    """Foydalanuvchining barcha majburiy kanallarga obuna bo'lganini tekshirish."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """Obunani tekshirish va kerak bo'lsa ogohlantirish."""
        user = event.from_user
        if user is None:
            return await handler(event, data)

        bot: Bot = data["bot"]
        channels = await ChannelModel.get_all()

        if not channels:
            # Majburiy obuna kanallari yo'q
            return await handler(event, data)

        # Har bir kanalni tekshirish
        not_subscribed = []
        for ch in channels:
            try:
                member = await bot.get_chat_member(
                    chat_id=ch["channel_id"],
                    user_id=user.id,
                )
                if member.status in (
                    ChatMemberStatus.LEFT,
                    ChatMemberStatus.KICKED,
                ):
                    not_subscribed.append(ch)
            except Exception as e:
                logger.warning(
                    "Kanal tekshirishda xatolik | channel=%s | xato=%s",
                    ch["channel_id"],
                    str(e),
                )

        if not_subscribed:
            await event.answer(
                "<b>\u25A0 Majburiy obuna</b>\n\n"
                "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n",
                reply_markup=subscription_keyboard(not_subscribed),
            )
            return  # Handlerga o'tkazmaslik

        return await handler(event, data)
