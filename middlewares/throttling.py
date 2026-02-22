"""
middlewares/throttling.py - Tezlikni cheklash (rate limiting) middleware.
Spam va flood xabarlarni oldini oladi.
"""

import time
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)

# Har bir foydalanuvchi uchun oxirgi xabar vaqtini saqlash
_user_last_message: Dict[int, float] = {}

# Minimal interval (soniyada)
THROTTLE_RATE: float = 0.5


class ThrottlingMiddleware(BaseMiddleware):
    """Foydalanuvchi xabarlarini tezlik bo'yicha cheklash."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """Agar foydalanuvchi juda tez xabar yuborayotgan bo'lsa, e'tiborga olmaslik."""
        user = event.from_user
        if user is None:
            return await handler(event, data)

        user_id = user.id
        now = time.time()
        last_time = _user_last_message.get(user_id, 0)

        if now - last_time < THROTTLE_RATE:
            logger.warning(
                "Throttle | user_id=%s | juda tez xabar yubormoqda", user_id
            )
            return  # Xabarni e'tiborga olmaslik

        _user_last_message[user_id] = now
        return await handler(event, data)
