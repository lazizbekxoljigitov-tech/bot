"""
handlers/user/comments.py - Izoh qoldirish handleri.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.comment import CommentStates
from models.user import UserModel
from models.comments import CommentsModel
from keyboards.inline import comments_list_keyboard, anime_view_keyboard
import math

logger = logging.getLogger(__name__)
router = Router(name="user_comments")

COMMENTS_PER_PAGE = 5

@router.callback_query(F.data.startswith("comment:"))
async def start_comment(callback: CallbackQuery, state: FSMContext) -> None:
    """Izoh yozish jarayonini boshlash."""
    anime_id = int(callback.data.split(":")[1])
    await state.set_state(CommentStates.waiting_text)
    await state.update_data(comment_anime_id=anime_id)
    await callback.message.answer("\u270E Izohingizni yozing:")
    await callback.answer()

@router.message(CommentStates.waiting_text)
async def save_comment(message: Message, state: FSMContext) -> None:
    """Izohni saqlash."""
    data = await state.get_data()
    await state.clear()
    anime_id = data.get("comment_anime_id")
    user = await UserModel.get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Avval /start buyrug'ini yuboring.")
        return
    await CommentsModel.add(user["id"], anime_id, message.text.strip())
    await message.answer("\u2714 Izohingiz qo'shildi!")

@router.callback_query(F.data.startswith("comments_list:"))
async def show_comments(callback: CallbackQuery) -> None:
    """Izohlar ro'yxatini ko'rsatish."""
    parts = callback.data.split(":")
    anime_id = int(parts[1])
    page = int(parts[2])
    total = await CommentsModel.get_comment_count(anime_id)
    total_pages = max(1, math.ceil(total / COMMENTS_PER_PAGE))
    offset = page * COMMENTS_PER_PAGE
    comments = await CommentsModel.get_by_anime(anime_id, COMMENTS_PER_PAGE, offset)

    if not comments:
        await callback.answer("Izohlar hali yo'q.")
        return

    text = f"<b>\u25A1 Izohlar</b> ({total} ta)\n\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n\n"
    for c in comments:
        name = c.get("full_name", "Foydalanuvchi")
        text += f"<b>{name}:</b>\n{c['comment_text']}\n\n"

    try:
        await callback.message.edit_text(
            text, reply_markup=comments_list_keyboard(anime_id, page, total_pages)
        )
    except Exception:
        await callback.message.answer(
            text, reply_markup=comments_list_keyboard(anime_id, page, total_pages)
        )
    await callback.answer()
