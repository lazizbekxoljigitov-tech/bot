"""
handlers/search/search.py - Anime qidirish handlerlari.
Emoji va chiroyli dizayn bilan.
"""

import logging
import math

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.search import SearchStates
from models.anime import AnimeModel
from models.user import UserModel
from models.favorites import FavoritesModel
from keyboards.reply import search_menu, user_main_menu, cancel_keyboard
from keyboards.inline import (
    search_results_keyboard,
    anime_view_keyboard,
)
from services.anime_service import AnimeService
from services.search_service import SearchService
from services.media_service import MediaService
from utils.images import IMAGES
from config import SEARCH_RESULTS_PER_PAGE, SEARCH_RESULTS_PER_PAGE

logger = logging.getLogger(__name__)
router = Router(name="user_search")


@router.message(F.text == "🔍 Anime qidirish")
@router.message(F.text == "/search")
async def show_search_menu(message: Message, state: FSMContext) -> None:
    """Qidiruv menyusini ko'rsatish."""
    await state.clear()
    try:
        await message.answer_photo(
            photo=IMAGES["SEARCH"],
            caption="<b>🔍 Anime qidirish</b>\n\nQidiruv turini tanlang:",
            reply_markup=search_menu(),
        )
    except Exception as e:
        logger.error(f"Error sending search photo: {e}")
        await message.answer(
            "<b>🔍 Anime qidirish</b>\n\nQidiruv turini tanlang:",
            reply_markup=search_menu(),
        )


@router.message(F.text == "📝 Nomi bo'yicha")
async def search_by_title_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_query)
    await message.answer(
        "📝 <b>Anime nomini kiriting:</b>",
        reply_markup=cancel_keyboard(),
    )


@router.message(F.text == "🔢 Kod bo'yicha")
async def search_by_code_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_code)
    await message.answer(
        "🔢 <b>Anime kodini kiriting:</b>",
        reply_markup=cancel_keyboard(),
    )


@router.message(F.text == "🎭 Janr bo'yicha")
async def search_by_genre_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_genre)
    await message.answer(
        "🎭 <b>Janr nomini kiriting:</b>\n(Masalan: Action, Romance, Drama)",
        reply_markup=cancel_keyboard(),
    )


@router.message(F.text == "🔥 Top Anime")
@router.message(F.text == "🌟 Top animelar")
async def search_top(message: Message) -> None:
    """Eng ko'p ko'rilgan animelar."""
    results, total_pages = await SearchService.get_top_anime(page=0)
    if not results:
        await message.answer("ℹ️ Hozircha animelar yo'q.")
        return
    
    # Premium formatlash
    text = (
        f"<b>🔥 Top Animelar</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Eng ko'p ko'rilgan qaynoq animelar:\n\n"
    )
    
    medals = ["🥇", "🥈", "🥉", "◈", "◈"]
    for i, anime in enumerate(results[:5]):
        medal = medals[i] if i < len(medals) else "◈"
        text += f"{medal} <b>{anime['title']}</b>\n   └ 👁 {anime['views']} • ⏳ {anime.get('status', '??')}\n"
    
    await message.answer(
        text,
        reply_markup=search_results_keyboard(results, 0, total_pages, "top", "all"),
    )


@router.message(F.text == "🆕 Yangi animelar")
async def search_new(message: Message) -> None:
    """Yangi qo'shilgan animelar."""
    results, total_pages = await SearchService.get_latest_anime(page=0)
    if not results:
        await message.answer("ℹ️ Hozircha animelar yo'q.")
        return
    await _show_search_results(message, results, 0, total_pages, "latest", "all")


@router.message(F.text == "💎 VIP animelar")
async def search_vip(message: Message) -> None:
    """Faqat VIP animelar."""
    results, total_pages = await SearchService.get_vip_anime(page=0)
    if not results:
        await message.answer("ℹ️ Hozircha VIP animelar yo'q.")
        return
    await _show_search_results(message, results, 0, total_pages, "vip", "all")



@router.message(F.text == "🎲 Tasodifiy anime")
async def search_random(message: Message) -> None:
    """Tasodifiy anime ko'rsatish."""
    anime = await SearchService.get_random_anime()
    if not anime:
        await message.answer("ℹ️ Hozircha animelar yo'q.")
        return
    await _show_anime_view(message, anime["id"])



@router.message(F.text == "⬅️ Orqaga")
async def back_to_main(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "<b>🏠 Bosh sahifa</b>",
        reply_markup=user_main_menu(),
    )


# ---- Qidiruv so'rovlarini qabul qilish ----

@router.message(SearchStates.waiting_query)
async def process_search_title(message: Message, state: FSMContext) -> None:
    query = message.text.strip()
    await state.clear()
    results, total_pages = await SearchService.search_by_title(query, page=0)
    if not results:
        await message.answer(f"ℹ️ <b>'{query}'</b> bo'yicha hech narsa topilmadi.", reply_markup=search_menu())
        return
    await _show_search_results(message, results, 0, total_pages, "title", query)


@router.message(SearchStates.waiting_code)
async def process_search_code(message: Message, state: FSMContext) -> None:
    code = message.text.strip().lower()
    await state.clear()
    anime = await AnimeModel.get_by_code(code)
    if not anime:
        await message.answer(f"❌ <b>Kod '{code}'</b> bo'yicha anime topilmadi.", reply_markup=search_menu())
        return
    # To'g'ridan-to'g'ri anime sahifasini ochish
    await _show_anime_view(message, anime["id"])


@router.message(SearchStates.waiting_genre)
async def process_search_genre(message: Message, state: FSMContext) -> None:
    genre = message.text.strip()
    await state.clear()
    results, total_pages = await SearchService.search_by_genre(genre, page=0)
    if not results:
        await message.answer(f"ℹ️ <b>'{genre}'</b> janrida animelar topilmadi.", reply_markup=search_menu())
        return
    await _show_search_results(message, results, 0, total_pages, "genre", genre)


# ---- Yordamchi funksiyalar ----

async def _show_search_results(message: Message, results: list, page: int, total_pages: int, q_type: str, q_val: str) -> None:
    """Qidiruv natijalarini inline keyboard bilan ko'rsatish."""
    text = (
        f"<b>🔍 Qidiruv natijalari:</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"Topildi: <b>{len(results)}</b> ta anime\n"
        f"Sahifa: <b>{page + 1}/{total_pages}</b>\n\n"
        f"◈ <i>Kerakli animeni tanlang:</i>"
    )
    await message.answer(
        text,
        reply_markup=search_results_keyboard(results, page, total_pages, q_type, q_val),
    )


async def _show_anime_view(message: Message, anime_id: int) -> None:
    """Anime sahifasini rasm va ma'lumotlar bilan ko'rsatish."""
    anime = await AnimeModel.get_by_id(anime_id)
    if not anime:
        await message.answer("❌ Anime topilmadi.")
        return

    await AnimeModel.increment_views(anime_id)
    db_user = await UserModel.get_by_telegram_id(message.from_user.id)
    is_fav = await FavoritesModel.is_favorite(db_user["id"], anime_id) if db_user else False
    
    text = await AnimeService.get_anime_info_text(anime_id)
    poster = AnimeService.get_poster(anime)
    
    if poster:
        try:
            await MediaService.send_photo(
                event=message,
                photo=poster,
                caption=text,
                reply_markup=anime_view_keyboard(anime_id, is_fav),
                context_info=f"Search View: {anime['title']} (ID: {anime_id})"
            )
        except Exception:
            await message.answer("❌ <b>Poster yuklashda xatolik yuz berdi. Adminlar ogohlantirildi.</b>")

    else:
        await message.answer(text, reply_markup=anime_view_keyboard(anime_id, is_fav))



# ---- Pagination Callbacklar ----

@router.callback_query(F.data.startswith("search_page:"))
async def process_search_pagination(callback: CallbackQuery) -> None:
    parts = callback.data.split(":")
    q_type = parts[1]
    q_val = parts[2]
    page = int(parts[3])
    
    offset = page * SEARCH_RESULTS_PER_PAGE
    
    if q_type == "title":
        results, total_pages = await SearchService.search_by_title(q_val, page=page)
    elif q_type == "genre":
        results, total_pages = await SearchService.search_by_genre(q_val, page=page)
    elif q_type == "top":
        results, total_pages = await SearchService.get_top_anime(page=page)
    elif q_type == "latest":
        results, total_pages = await SearchService.get_latest_anime(page=page)
    elif q_type == "vip":
        results, total_pages = await SearchService.get_vip_anime(page=page)
    else:
        await callback.answer("❌ Xatolik!")
        return

    await callback.message.edit_reply_markup(
        reply_markup=search_results_keyboard(results, page, total_pages, q_type, q_val)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("anime_details:"))
async def show_anime_callback(callback: CallbackQuery) -> None:
    """Natijalardan anime tanlanganda ko'rsatish (Seamless Audit)."""
    anime_id = int(callback.data.split(":")[1])
    
    anime = await AnimeModel.get_by_id(anime_id)
    if not anime:
        await callback.answer("Anime topilmadi.")
        return

    await AnimeModel.increment_views(anime_id)
    db_user = await UserModel.get_by_telegram_id(callback.from_user.id)
    is_fav = await FavoritesModel.is_favorite(db_user["id"], anime_id) if db_user else False
    
    text = await AnimeService.get_anime_info_text(anime_id)
    poster = AnimeService.get_poster(anime)
    
    # Switch from Search Result Text to Anime Poster Seamlessly
    success = await MediaService.replace_media_with_photo(
        callback=callback,
        photo=poster,
        caption=text,
        reply_markup=anime_view_keyboard(anime_id, is_fav),
        context_info=f"Search Detail View: {anime['title']} (ID: {anime_id})"
    )
    
    if not success:
        # Fallback to answer_photo if editing text to photo fails
        await MediaService.send_photo(
            event=callback,
            photo=poster,
            caption=text,
            reply_markup=anime_view_keyboard(anime_id, is_fav),
            context_info=f"Search Detail View Fallback: {anime['title']} (ID: {anime_id})"
        )
        try:
            await callback.message.delete()
        except Exception:
            pass

    await callback.answer()
