"""
handlers/admin/broadcast.py - Barcha foydalanuvchilarga xabar yuborish (Broadcast).
"""

import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from models.user import UserModel
from models.admin import AdminModel
from utils.images import IMAGES
from keyboards.reply import cancel_keyboard, admin_main_menu, confirm_keyboard
from filters.admin import is_admin


logger = logging.getLogger(__name__)
router = Router(name="admin_broadcast")

class BroadcastStates(StatesGroup):
    waiting_message = State()
    confirm = State()



@router.message(F.text == "📤 Xabar yuborish", is_admin)
@router.callback_query(F.data == "admin_broadcast", is_admin)
async def broadcast_start(event: Message | CallbackQuery, state: FSMContext) -> None:
    """Xabar yuborishni boshlash."""
    await state.set_state(BroadcastStates.waiting_message)
    caption = (
        "📤 <b>XABAR YUBORISH</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📝 Yubormoqchi bo'lgan xabaringizni yuboring:\n\n"
        "<i>(Matn, rasm, video yoki istalgan media turini yuborishingiz mumkin)</i>"
    )
    
    kb = cancel_keyboard()
    
    from services.media_service import MediaService
    try:
        if isinstance(event, Message):
            await MediaService.send_photo(
                event=event,
                photo=IMAGES["BROADCAST"],
                caption=caption,
                reply_markup=kb,
                context_info="Broadcast Start"
            )
        else:
            await MediaService.send_photo(
                event=event.message,
                photo=IMAGES["BROADCAST"],
                caption=caption,
                reply_markup=kb,
                context_info="Broadcast Start (Callback)"
            )
            await event.message.delete()
            await event.answer()
    except Exception:
        if isinstance(event, Message):
            await event.answer(caption, reply_markup=kb)
        else:
            await event.message.answer(caption, reply_markup=kb)
            await event.message.delete()
            await event.answer()


@router.message(BroadcastStates.waiting_message, is_admin)
async def broadcast_preview(message: Message, state: FSMContext) -> None:
    """Xabar previewsi."""
    await state.update_data(broadcast_message_id=message.message_id, from_chat_id=message.chat.id)
    await state.set_state(BroadcastStates.confirm)
    
    await message.answer("👆 <b>Yuboriladigan xabar yuqoridagidek ko'rinadi.</b>")
    await message.answer(
        "✅ <b>Xabarni barcha foydalanuvchilarga yuborishni tasdiqlaysizmi?</b>",
        reply_markup=confirm_keyboard()
    )

@router.message(BroadcastStates.confirm, F.text == "✅ Tasdiqlash", is_admin)
async def broadcast_process(message: Message, state: FSMContext, bot: Bot) -> None:
    """Xabarni yuborish jarayoni."""
    data = await state.get_data()
    await state.clear()
    
    message_id = data['broadcast_message_id']
    from_chat_id = data['from_chat_id']
    
    users = await UserModel.get_all_users()
    total = len(users)
    sent = 0
    blocked = 0
    errors = 0
    
    status_msg = await message.answer(
        f"⏳ <b>Yuborish boshlandi...</b>\n"
        f"Jami: {total} foydalanuvchi"
    )
    
    for i, user in enumerate(users):
        try:
            await bot.copy_message(
                chat_id=user['telegram_id'],
                from_chat_id=from_chat_id,
                message_id=message_id
            )
            sent += 1
        except TelegramForbiddenError:
            blocked += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            # Retry
            try:
                await bot.copy_message(
                    chat_id=user['telegram_id'],
                    from_chat_id=from_chat_id,
                    message_id=message_id
                )
                sent += 1
            except Exception:
                errors += 1
        except Exception as e:
            logger.error(f"Broadcast error to {user['telegram_id']}: {e}")
            errors += 1
            
        # Update status every 50 users
        if (i + 1) % 50 == 0:
            try:
                await status_msg.edit_text(
                    f"⏳ <b>Yuborish davom etmoqda... ({i+1}/{total})</b>\n\n"
                    f"✅ Yuborildi: {sent}\n"
                    f"🚫 Bloklagan: {blocked}\n"
                    f"❌ Xatolik: {errors}"
                )
            except Exception:
                pass
        
        # Anti-flood delay
        await asyncio.sleep(0.05)

    await status_msg.answer(
        f"🏁 <b>Yuborish yakunlandi!</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ <b>Yuborildi:</b> {sent}\n"
        f"🚫 <b>Bloklagan:</b> {blocked}\n"
        f"❌ <b>Xatolik:</b> {errors}\n\n"
        f"Jami: {total}",
        reply_markup=admin_main_menu()
    )
    await status_msg.delete()
