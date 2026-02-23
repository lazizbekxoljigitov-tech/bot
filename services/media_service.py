"""
services/media_service.py - Media (photo/video) delivery service.
Handles sending media with robust error handling and automated admin alerting.
"""

import logging
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

class MediaService:
    @staticmethod
    async def send_photo(
        event: Message | CallbackQuery, 
        photo: str, 
        caption: str, 
        reply_markup=None, 
        context_info: str = ""
    ) -> bool:
        """Send a photo and notify admin if it fails."""
        bot: Bot = event.bot
        target = event if isinstance(event, Message) else event.message
        
        try:
            await target.answer_photo(
                photo=photo,
                caption=caption,
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            error_msg = f"‼️ <b>MEDIA XATOLIGI (PHOTO)</b>\n\n" \
                        f"📍 <b>Joy:</b> {context_info}\n" \
                        f"❌ <b>Xato:</b> {str(e)}\n" \
                        f"🔗 <b>Fayl:</b> <code>{photo}</code>"
            
            logger.error(f"Media error (photo): {e} | Context: {context_info}")
            
            # Notify admins
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, error_msg)
                except Exception:
                    pass
            
            # Re-raise to let the handler know it failed (user doesn't want text-only fallback)
            raise e

    @staticmethod
    async def send_video(
        event: Message | CallbackQuery, 
        video: str, 
        caption: str, 
        reply_markup=None, 
        context_info: str = ""
    ) -> bool:
        """Send a video and notify admin if it fails."""
        bot: Bot = event.bot
        target = event if isinstance(event, Message) else event.message
        
        try:
            await target.answer_video(
                video=video,
                caption=caption,
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            error_msg = f"‼️ <b>MEDIA XATOLIGI (VIDEO)</b>\n\n" \
                        f"📍 <b>Joy:</b> {context_info}\n" \
                        f"❌ <b>Xato:</b> {str(e)}\n" \
                        f"🔗 <b>Fayl:</b> <code>{video}</code>"
            
            logger.error(f"Media error (video): {e} | Context: {context_info}")
            
            # Notify admins
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, error_msg)
                except Exception:
                    pass
            
            raise e
