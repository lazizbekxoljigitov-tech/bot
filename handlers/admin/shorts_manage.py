"""
handlers/admin/shorts_manage.py - Shorts boshqarish handleri (admin).
Short videolar qo'shish va o'chirish.
"""

import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from states.shorts import AddShortsStates
from models.anime import AnimeModel
from models.shorts import ShortsModel
from models.admin import AdminModel
from keyboards.reply import cancel_keyboard, admin_main_menu
from keyboards.inline import anime_select_keyboard

logger = logging.getLogger(__name__)
router = Router(name="admin_shorts")


async def is_admin(message: Message) -> bool:
    return await AdminModel.is_admin(message.from_user.id)


@router.message(F.text == "🎬 Shorts qo'shish", is_admin)
async def add_short_start(message: Message, state: FSMContext) -> None:
    """Short qo'shish - anime tanlash."""
    anime_list = await AnimeModel.get_all(limit=50)
    if not anime_list:
        await message.answer("\u25B8 Avval anime qo'shing.")
        return
    await state.set_state(AddShortsStates.select_anime)
    await message.answer(
        "<b>🎬 Shorts qo'shish</b>\n\nQaysi animega short qo'shmoqchisiz?",
        reply_markup=anime_select_keyboard(anime_list, "add_short_anime"),
    )


@router.callback_query(F.data.startswith("add_short_anime:"))
async def add_short_anime_selected(callback: CallbackQuery, state: FSMContext) -> None:
    """Short uchun anime tanlangan."""
    anime_id = int(callback.data.split(":")[1])
    await state.update_data(anime_id=anime_id)
    await state.set_state(AddShortsStates.video)

    anime = await AnimeModel.get_by_id(anime_id)
    await callback.message.edit_text(
        f"<b>{anime['title']}</b>\n\n"
        "\u25B8 Qisqa videoni yuboring:"
    )
    await callback.answer()


@router.message(AddShortsStates.video, is_admin, F.video)
async def add_short_video(message: Message, state: FSMContext) -> None:
    """Short videoni qabul qilish va saqlash."""
    data = await state.get_data()
    await state.clear()

    try:
        short_id = await ShortsModel.create(data["anime_id"], file_id)
        anime = await AnimeModel.get_by_id(data["anime_id"])
        await message.answer(
            f"✔ <b>Short qo'shildi!</b>\n\n"
            f"▸ Anime: {anime['title'] if anime else '---'}\n"
            f"▸ ID: {short_id}",
            reply_markup=admin_main_menu(),
        )
    except Exception as e:
        logger.error(f"Short create error: {e}")
        await message.answer(
            f"✖ <b>Qo'shishda xatolik!</b>\n"
            f"Xato: <code>{str(e)}</code>",
            reply_markup=admin_main_menu()
        )



@router.message(AddShortsStates.video, is_admin)
async def add_short_video_invalid(message: Message, state: FSMContext) -> None:
    """Video bo'lmagan xabar."""
    await message.answer("\u25B8 Iltimos, video fayl yuboring.")
