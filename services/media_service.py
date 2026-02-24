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
                        f"👤 <b>User:</b> <a href='tg://user?id={event.from_user.id}'>{event.from_user.full_name}</a> (<code>{event.from_user.id}</code>)\n" \
                        f"📍 <b>Joy:</b> {context_info}\n" \
                        f"❌ <b>Xato:</b> <code>{str(e)}</code>\n" \
                        f"🔗 <b>Fayl:</b> <code>{photo}</code>"
            
            logger.error(f"Media error (photo): {e} | User: {event.from_user.id} | Context: {context_info}")
            
            # Notify admins with possible fix button
            from keyboards.inline import admin_fix_media_keyboard
            fix_kb = admin_fix_media_keyboard(context_info, "photo")
            
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, error_msg, reply_markup=fix_kb, parse_mode="HTML")
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
                        f"👤 <b>User:</b> <a href='tg://user?id={event.from_user.id}'>{event.from_user.full_name}</a> (<code>{event.from_user.id}</code>)\n" \
                        f"📍 <b>Joy:</b> {context_info}\n" \
                        f"❌ <b>Xato:</b> <code>{str(e)}</code>\n" \
                        f"🔗 <b>Fayl:</b> <code>{video}</code>"
            
            logger.error(f"Media error (video): {e} | User: {event.from_user.id} | Context: {context_info}")
            
            from keyboards.inline import admin_fix_media_keyboard
            fix_kb = admin_fix_media_keyboard(context_info, "video")
            
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, error_msg, reply_markup=fix_kb, parse_mode="HTML")
                except Exception:
                    pass

            
            raise e

    @staticmethod
    async def edit_photo_caption(
        callback: CallbackQuery,
        caption: str,
        reply_markup=None,
        context_info: str = ""
    ) -> bool:
        """Edit an existing photo's caption with fallback to edit_text/answer."""
        try:
            await callback.message.edit_caption(
                caption=caption,
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            logger.info(f"Failed to edit photo caption, trying edit_text: {e}")
            try:
                await callback.message.edit_text(
                    text=caption,
                    reply_markup=reply_markup
                )
                return True
            except Exception as e2:
                logger.debug(f"Failed to edit text, trying answer: {e2}")
                try:
                    await callback.message.answer(
                        text=caption,
                        reply_markup=reply_markup
                    )
                    return True
                except Exception as e3:
                    logger.error(f"MediaService error (edit_photo_caption): {e3} | Context: {context_info}")
                    return False

    @staticmethod
    async def edit_video_caption(
        callback: CallbackQuery,
        caption: str,
        reply_markup=None,
        context_info: str = ""
    ) -> bool:
        """Edit an existing video's caption with fallback to edit_text/answer."""
        try:
            await callback.message.edit_caption(
                caption=caption,
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            logger.info(f"Failed to edit video caption, trying edit_text: {e}")
            try:
                await callback.message.edit_text(
                    text=caption,
                    reply_markup=reply_markup
                )
                return True
            except Exception as e2:
                logger.debug(f"Failed to edit text, trying answer: {e2}")
                try:
                    await callback.message.answer(
                        text=caption,
                        reply_markup=reply_markup
                    )
                    return True
                except Exception as e3:
                    logger.error(f"MediaService error (edit_video_caption): {e3} | Context: {context_info}")
                    return False

    @staticmethod
    async def send_photo_to_chat(
        bot: Bot,
        chat_id: int,
        photo: str,
        caption: str,
        reply_markup=None,
        context_info: str = ""
    ) -> bool:
        """Send a photo to a specific chat ID (usually for admins)."""
        try:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send photo to chat {chat_id}: {e} | Context: {context_info}")
            return False
