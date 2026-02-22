"""
handlers/comments/comments.py - Izohlarni boshqarish va ko'rish.
Emoji va premium dizayn bilan.
"""

import math
import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.comment import CommentStates
from models.comment import CommentModel
from models.user import UserModel
from keyboards.reply import cancel_keyboard, user_main_menu
from keyboards.inline import comments_list_keyboard
from config import COMMENTS_PER_PAGE

logger = logging.getLogger(__name__)
router = Router(name="user_comments")


@router.callback_query(F.data.startswith("comment:"))
async def leave_comment_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Izoh qoldirishni boshlash."""
    anime_id = int(callback.data.split(":")[1])
    await state.set_state(CommentStates.waiting_text)
    await state.update_data(comment_anime_id=anime_id)
    
    await callback.message.answer(
        "✍️ <b>Ushbu anime haqida o'z fikringizni yozing:</b>",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(CommentStates.waiting_text)
async def process_comment_text(message: Message, state: FSMContext) -> None:
    """Izoh matnini saqlash."""
    data = await state.get_data()
    anime_id = data.get("comment_anime_id")
    text = message.text.strip()
    
    user = await UserModel.get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("❌ Xatolik!")
        return

    await CommentModel.add(user["id"], anime_id, text)
    await state.clear()
    
    await message.answer(
        "✅ <b>Izohingiz muvaffaqiyatli saqlandi!</b>",
        reply_markup=user_main_menu(),
    )


@router.callback_query(F.data.startswith("comments_list:"))
async def show_comments(callback: CallbackQuery) -> None:
    """Izohlar ro'yxatini ko'rsatish."""
    parts = callback.data.split(":")
    anime_id = int(parts[1])
    page = int(parts[2])
    
    total_count = await CommentModel.get_count(anime_id)
    total_pages = max(1, math.ceil(total_count / COMMENTS_PER_PAGE))
    offset = page * COMMENTS_PER_PAGE
    
    comments = await CommentModel.get_by_anime(
        anime_id, limit=COMMENTS_PER_PAGE, offset=offset
    )
    
    if not comments:
        await callback.answer("💬 Izohlar hali yo'q.", show_alert=True)
        return

    text = (
        f"<b>💬 Izohlar</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    for c in comments:
        vip_badge = " 💎 VIP" if c.get("is_vip") else ""
        text += (
            f"👤 <b>{c['full_name']}</b>{vip_badge}\n"
            f"📝 {c['text']}\n"
            f"🕒 <i>{c['created_at']}</i>\n"
            f"━━━━━━━━━━━━\n"
        )
    
    text += f"\n📄 Sahifa: {page + 1}/{total_pages}"
    
    try:
        await callback.message.edit_text(
            text, reply_markup=comments_list_keyboard(anime_id, page, total_pages)
        )
    except Exception:
        await callback.message.answer(
            text, reply_markup=comments_list_keyboard(anime_id, page, total_pages)
        )
        
    await callback.answer()
