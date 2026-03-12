"""
handlers/episodes/view.py - Qismlar ko'rish handleri.
Sezon tanlash, qism tanlash, VIP tekshirish va video yuborish.
"""

import logging
import math

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from models.anime import AnimeModel
from models.episode import EpisodeModel
from services.anime_service import AnimeService
from services.vip_service import VipService
from services.user_service import UserService
from utils.images import IMAGES
from keyboards.inline import seasons_keyboard, episodes_keyboard, episode_view_keyboard, vip_plans_keyboard
from config import EPISODES_PER_PAGE
from services.media_service import MediaService


from models.favorites import FavoritesModel
from models.user import UserModel


logger = logging.getLogger(__name__)
router = Router(name="episodes_view")


@router.callback_query(F.data.startswith("anime_details:"))
async def show_anime_details(callback: CallbackQuery) -> None:
    """Anime ma'lumotlarini qayta ko'rsatish (Seamless 'Back' navigation)."""
    anime_id = int(callback.data.split(":")[1])
    anime = await AnimeModel.get_by_id(anime_id)
    
    if not anime:
        await callback.answer("Anime topilmadi.")
        return

    # Sevimlilarda bormi-yo'qligini tekshirish
    db_user = await UserModel.get_by_telegram_id(callback.from_user.id)
    is_fav = await FavoritesModel.is_favorite(db_user["id"], anime_id) if db_user else False
    
    text = await AnimeService.get_anime_info_text(anime_id)
    poster = AnimeService.get_poster(anime)
    
    # Silliq almashuv (Video/Photo -> Photo)
    success = await MediaService.replace_media_with_photo(
        callback=callback,
        photo=poster,
        caption=text,
        reply_markup=anime_view_keyboard(anime_id, is_fav),
        context_info=f"Anime Details (Back): {anime['title']} (ID: {anime_id})"
    )
    
    if not success:
        # Agar rasm bo'lmasa yoki edit xato bersa, shunchaki xabar yuboramiz
        await callback.message.answer(text, reply_markup=anime_view_keyboard(anime_id, is_fav))
    
    await callback.answer()


@router.callback_query(F.data.startswith("watch:"))
async def show_seasons(callback: CallbackQuery) -> None:
    """Anime sezonlarini ko'rsatish (Skip if single season)."""
    anime_id = int(callback.data.split(":")[1])
    anime = await AnimeModel.get_by_id(anime_id)

    if not anime:
        await callback.answer("Anime topilmadi.")
        return

    seasons = await EpisodeModel.get_seasons(anime_id)

    if not seasons:
        await callback.answer("Bu anime uchun qismlar hali qo'shilmagan.")
        return

    # Agar faqat bitta sezon bo'lsa, to'g'ridan-to'g'ri qismlarni ko'rsatamiz
    if len(seasons) == 1:
        await _show_episodes_internal(callback, anime, seasons[0], 0, True)
        return

    text = (
        f"<b>{anime['title']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🎞 <b>Sezonni tanlang:</b>"
    )

    await MediaService.edit_photo_caption(
        callback=callback,
        caption=text,
        reply_markup=seasons_keyboard(anime_id, seasons),
        context_info="Sezon tanlash"
    )

    await callback.answer()


@router.callback_query(F.data.startswith("season:"))
async def show_episodes(callback: CallbackQuery) -> None:
    """Sezon qismlarini ko'rsatish (paginatsiya bilan)."""
    parts = callback.data.split(":")
    anime_id = int(parts[1])
    season = int(parts[2])
    page = int(parts[3])

    anime = await AnimeModel.get_by_id(anime_id)
    if not anime:
        await callback.answer("Anime topilmadi.")
        return

    # Sezonlar sonini tekshirib, bittalik ekanligini bilib olamiz
    seasons = await EpisodeModel.get_seasons(anime_id)
    is_single_season = len(seasons) <= 1

    await _show_episodes_internal(callback, anime, season, page, is_single_season)


async def _show_episodes_internal(callback: CallbackQuery, anime: dict, season: int, page: int, is_single_season: bool) -> None:
    """Qismlarni ko'rsatish uchun ichki funksiya (Seamless)."""
    anime_id = anime["id"]
    total_count = await EpisodeModel.get_episode_count(anime_id, season)
    total_pages = max(1, math.ceil(total_count / EPISODES_PER_PAGE))
    offset = page * EPISODES_PER_PAGE

    episodes = await EpisodeModel.get_by_season(
        anime_id, season, limit=EPISODES_PER_PAGE, offset=offset
    )

    if not episodes:
        await callback.answer("Bu sezonda qismlar topilmadi.")
        return

    text = (
        f"<b>{anime['title']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>🎞 Jami:</b> {total_count}\n\n"
        f"<b>Marhamat, tanlang:</b>"
    )

    await MediaService.edit_photo_caption(
        callback=callback,
        caption=text,
        reply_markup=episodes_keyboard(anime_id, season, episodes, page, total_pages, is_single_season),
        context_info="Qism tanlash"
    )

    await callback.answer()


@router.callback_query(F.data.startswith("episode:"))
async def watch_episode(callback: CallbackQuery, state: FSMContext) -> None:
    """Qismni tomosha qilish - videoni yuborish."""
    episode_id = int(callback.data.split(":")[1])
    episode = await EpisodeModel.get_by_id(episode_id)

    if not episode:
        await callback.answer("Qism topilmadi.")
        return

    anime = await AnimeModel.get_by_id(episode["anime_id"])
    if not anime:
        await callback.answer("Anime topilmadi.")
        return

    # VIP tekshirish (anime yoki qism VIP bo'lsa)
    if anime["is_vip"] or episode["is_vip"]:
        is_vip = await UserService.is_vip_active(callback.from_user.id)
        if not is_vip:
            # Plan tanlashdan oldin anime kontekstini saqlab qo'yamiz
            await state.update_data(context_anime_id=anime["id"], context_anime_title=anime["title"])
            
            plans = await VipModel.get_all_plans()
            plans_text = await VipService.get_plans_text(anime_title=anime["title"])
            kb = vip_plans_keyboard(plans, anime_title=anime["title"]) if plans else None
            
            # Posterni o'chirib, VIP rejalarni ko'rsatish
            try:
                await callback.message.answer_photo(
                    photo=IMAGES["VIP"],
                    caption=plans_text,
                    reply_markup=kb
                )
                await callback.message.delete()
            except Exception:
                await callback.message.answer(plans_text, reply_markup=kb)
            
            await callback.answer("\u25C6 VIP a'zolik talab etiladi.")
            return

    # Ko'rishlar sonini oshirish
    await EpisodeModel.increment_views(episode_id)

    # Qism ma'lumotlarini formatlash
    text = await AnimeService.format_episode_text(episode, anime)

    # Seamless media replacement (Edit Photo -> Video)
    success = await MediaService.replace_media_with_video(
        callback=callback,
        video=episode["video_file_id"],
        caption=text,
        reply_markup=episode_view_keyboard(anime["id"], episode_id),
        context_info=f"Episode: {anime['title']} S{episode['season_number']}E{episode['episode_number']} (ID: {episode_id})"
    )
    
    if not success:
        await callback.message.answer("❌ <b>Videoni yuklab bo'lmadi. Adminlar ogohlantirildi.</b>")
    
    await callback.answer()

