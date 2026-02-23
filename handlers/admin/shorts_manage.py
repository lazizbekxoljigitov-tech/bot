"""
handlers/admin/shorts_manage.py - Shorts boshqarish handleri (admin).
Short videolar qo'shish va o'chirish.
"""

import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from states.shorts import AddShortsStates, EditShortsStates
from models.anime import AnimeModel
from models.shorts import ShortsModel
from models.admin import AdminModel
from keyboards.reply import cancel_keyboard, admin_main_menu
from keyboards.inline import anime_select_keyboard, shorts_manage_keyboard, short_action_keyboard


logger = logging.getLogger(__name__)
router = Router(name="admin_shorts")


async def is_admin(message: Message) -> bool:
    return await AdminModel.is_admin(message.from_user.id)


@router.message(F.text == "🎬 Shorts boshqarish", is_admin)
@router.callback_query(F.data == "admin_manage_shorts", is_admin)
async def manage_shorts_start(event: Message | CallbackQuery) -> None:
    """Shorts boshqarish menyusi."""
    shorts = await ShortsModel.get_all(limit=100)
    text = (
        "<b>🎬 Shorts Boshqarish</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"Jami: {len(shorts)} ta short video mavjud.\n"
        "Boshqarish uchun shortni tanlang:"
    )
    kb = shorts_manage_keyboard(shorts)
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)
        await event.answer()


@router.callback_query(F.data == "add_short_direct", is_admin)
async def add_short_direct(callback: CallbackQuery, state: FSMContext) -> None:
    """Boshqaruvdan to'g'ridan-to'g'ri qo'shish."""
    await add_short_start(callback.message, state)
    await callback.answer()


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
        short_id = await ShortsModel.create(data["anime_id"], message.video.file_id)


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
    await message.answer("▸ Iltimos, video fayl yuboring.")


# ==============================================================
# SHORTS TAHRIRLASH VA O'CHIRISH
# ==============================================================

@router.callback_query(F.data.startswith("manage_short:"), is_admin)
async def manage_single_short(callback: CallbackQuery) -> None:
    """Bitta shortni boshqarish."""
    short_id = int(callback.data.split(":")[1])
    short = await ShortsModel.get_by_id(short_id)
    if not short:
        await callback.answer("Short topilmadi.")
        return
        
    text = (
        f"<b>🎬 Shorts: {short['anime_title']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 <b>ID:</b> <code>{short['id']}</code>\n"
        f"👁 <b>Ko'rilgan:</b> {short['views']}\n"
        f"🔗 <b>Fayl ID:</b> <code>{short['short_video_file_id']}</code>\n\n"
        "Amalni tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=short_action_keyboard(short_id))
    await callback.answer()


@router.callback_query(F.data.startswith("edit_short_video:"), is_admin)
@router.callback_query(F.data.startswith("fix_short:"), is_admin)
async def edit_short_video_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Short videosini yangilash boshlash."""
    short_id = int(callback.data.split(":")[1])
    await state.update_data(edit_short_id=short_id)
    await state.set_state(EditShortsStates.waiting_video)
    
    await callback.message.edit_text(
        "🎬 <b>Videoni yangilash</b>\n\nYangi video faylni yuboring:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@router.message(EditShortsStates.waiting_video, is_admin, F.video)
async def process_edit_short_video(message: Message, state: FSMContext) -> None:
    """Yangi videoni saqlash."""
    data = await state.get_data()
    short_id = data["edit_short_id"]
    file_id = message.video.file_id
    
    await state.clear()
    
    try:
        # ShortsModel da update metodi yo'q ekan, hozircha delete+create qilsak bo'ladi
        # Yoki shunchaki SQL execute qilsak bo'ladi. Direct SQL dan foydalanamiz (mukammallik uchun modelga metod qo'shamiz keyinroq)
        from database import Database
        db = await Database.connect()
        await db.execute(
            "UPDATE shorts SET short_video_file_id = ? WHERE id = ?",
            (file_id, short_id)
        )
        await db.commit()
        
        await message.answer(
            f"✅ <b>Short video muvaffaqiyatli yangilandi!</b> (ID: {short_id})",
            reply_markup=admin_main_menu()
        )
    except Exception as e:
        logger.error(f"Short update error: {e}")
        await message.answer(f"✖ <b>Xatolik:</b> {e}", reply_markup=admin_main_menu())


@router.callback_query(F.data.startswith("delete_short_confirm:"), is_admin)
async def delete_short_process(callback: CallbackQuery) -> None:
    """Shortni o'chirish."""
    short_id = int(callback.data.split(":")[1])
    try:
        # ShortsModel da delete ham yo'q ekan, qo'shib ketamiz
        from database import Database
        db = await Database.connect()
        await db.execute("DELETE FROM shorts WHERE id = ?", (short_id,))
        await db.execute("DELETE FROM shorts_views WHERE short_id = ?", (short_id,))
        await db.commit()
        
        await callback.answer("✅ Short o'chirildi.")
        await manage_shorts_start(callback)
    except Exception as e:
        logger.error(f"Short delete error: {e}")
        await callback.answer(f"✖ Xatolik: {e}", show_alert=True)

