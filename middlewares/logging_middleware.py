"""
middlewares/logging_middleware.py - Barcha update'larni loglash middleware.
Har bir xabar va callback haqida log yozadi.
"""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Har bir kiruvchi update haqida log yozuvchi middleware."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        """Update ma'lumotlarini loglab, handlerga uzatish."""
        if event.message:
            user = event.message.from_user
            logger.info(
                "Xabar | user_id=%s | username=%s | text=%s",
                user.id if user else "N/A",
                user.username if user else "N/A",
                event.message.text[:50] if event.message.text else "[media]",
            )
        elif event.callback_query:
            user = event.callback_query.from_user
            logger.info(
                "Callback | user_id=%s | username=%s | data=%s",
                user.id if user else "N/A",
                user.username if user else "N/A",
                event.callback_query.data,
            )

        return await handler(event, data)
