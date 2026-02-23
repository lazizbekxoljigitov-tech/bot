"""
handlers/user/start.py - /start buyrug'i va asosiy menyu handleri.
Premium dizayn va chiroyli kutib olish xabari.
"""

import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from models.user import UserModel
from models.anime import AnimeModel
from models.favorites import FavoritesModel
from models.admin import AdminModel
from keyboards.reply import user_main_menu, admin_main_menu
from keyboards.inline import anime_view_keyboard
from services.anime_service import AnimeService
from services.user_service import UserService
from utils.images import IMAGES
from config import ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router(name="user_start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    /start buyrug'i handleri.
    Foydalanuvchini ro'yxatdan o'tkazadi va deep linklarni qayta ishlaydi.
    """
    await state.clear()
    user = message.from_user

    # Foydalanuvchini ro'yxatdan o'tkazish
    await UserModel.create_or_update(
        telegram_id=user.id,
        full_name=user.full_name or "",
        username=user.username or "",
    )

    # VIP tekshirish
    await UserService.check_and_expire_vip(user.id)

    # Deep link argumentlarini tekshirish
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        param = args[1]

        # anime_123 -> Anime sahifasi
        if param.startswith("anime_"):
            try:
                anime_id = int(param.replace("anime_", ""))
                anime = await AnimeModel.get_by_id(anime_id)
                if anime:
                    await AnimeModel.increment_views(anime_id)
                    db_user = await UserModel.get_by_telegram_id(user.id)
                    is_fav = await FavoritesModel.is_favorite(
                        db_user["id"], anime_id
                    ) if db_user else False
                    
                    text = await AnimeService.get_anime_info_text(anime_id)
                    poster = AnimeService.get_poster(anime)
                    
                    if poster:
                        try:
                            await message.answer_photo(
                                photo=poster,
                                caption=text,
                                reply_markup=anime_view_keyboard(anime_id, is_fav),
                            )
                        except Exception as e:
                            logger.error(f"Poster yuborishda xato (anime_{anime_id}): {e}")
                            await message.answer(
                                text, reply_markup=anime_view_keyboard(anime_id, is_fav)
                            )
                    else:
                        await message.answer(
                            text, reply_markup=anime_view_keyboard(anime_id, is_fav)
                        )

                    return
            except (ValueError, TypeError):
                pass

        # fav_123 -> Sevimlilarga qo'shish
        if param.startswith("fav_"):
            try:
                anime_id = int(param.replace("fav_", ""))
                db_user = await UserModel.get_by_telegram_id(user.id)
                if db_user:
                    added = await FavoritesModel.add(db_user["id"], anime_id)
                    if added:
                        await message.answer("⭐️ <b>Muvaffaqiyatli sevimlilarga qo'shildi!</b>")
                    else:
                        await message.answer("ℹ️ <b>Bu anime allaqachon sevimlilaringizda mavjud.</b>")
                return
            except (ValueError, TypeError):
                pass

    # Xush kelibsiz xabari
    welcome_text = (
        f"<b>👋 As-salomu alaykum, {user.full_name}!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"◈ <b>AnimeBot-ga xush kelibsiz!</b>\n"
        f"▹ Siz bu yerda eng sara va ommabop animelarni\n"
        f"▹ O'zbek tilida, HD sifatda tomosha qilishingiz mumkin.\n\n"
        f"⬇️ <b>Kerakli bo'limni tanlang:</b>"
    )
    
    try:
        await message.answer_photo(
            photo=IMAGES["WELCOME"],
            caption=welcome_text,
            reply_markup=user_main_menu(),
        )
    except Exception as e:
        logger.error(f"Xush kelibsiz rasmini (WELCOME) yuborishda xato: {e}")
        await message.answer(
            welcome_text,
            reply_markup=user_main_menu(),
        )


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    """/admin buyrug'i - admin panelni ochish."""
    await state.clear()
    if await AdminModel.is_admin(message.from_user.id):
        await message.answer(
            "<b>⚙️ Admin panel</b>\n\n"
            "Admin menyusidan kerakli bo'limni tanlang.",
            reply_markup=admin_main_menu(),
        )
    else:
        await message.answer("❌ <b>Sizda admin paneliga ruxsat yo'q.</b>")


@router.message(F.text == "🏠 Bosh sahifa")
@router.message(F.text == "\u2302 Bosh sahifa")
async def home_page(message: Message, state: FSMContext) -> None:
    """Bosh sahifaga qaytish."""
    await state.clear()
    await message.answer(
        "<b>🏠 Bosh sahifa</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=user_main_menu(),
    )


@router.message(F.text == "⬅️ Orqaga")
async def go_back(message: Message, state: FSMContext) -> None:
    """Orqaga qaytish."""
    await state.clear()
    await message.answer(
        "<b>🏠 Bosh sahifa</b>",
        reply_markup=user_main_menu(),
    )


@router.message(F.text == "❌ Bekor qilish")
async def cancel_action(message: Message, state: FSMContext) -> None:
    """Amalni bekor qilish."""
    await state.clear()
    is_admin = await AdminModel.is_admin(message.from_user.id)
    kb = admin_main_menu() if is_admin else user_main_menu()
    await message.answer(
        "❌ <b>Amal bekor qilindi.</b>",
        reply_markup=kb,
    )


@router.message(F.text == "⬅️ Foydalanuvchi paneli")
async def back_to_user(message: Message, state: FSMContext) -> None:
    """Admin panelidan user paneliga o'tish."""
    await state.clear()
    await message.answer(
        "👤 <b>Foydalanuvchi paneli</b>",
        reply_markup=user_main_menu(),
    )


@router.callback_query(F.data == "back_to_menu")
async def callback_back(callback: CallbackQuery, state: FSMContext) -> None:
    """Menyuga qaytish callbacki."""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "<b>🏠 Bosh sahifa</b>",
        reply_markup=user_main_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "check_subscription")
async def check_sub(callback: CallbackQuery) -> None:
    """Obunani tekshirish."""
    # Bu yerda aslida haqiqiy tekshiruv middleware'da
    await callback.message.answer(
        "<b>✅ Obuna tasdiqlandi!</b>\n\nFoydalanishda davom eting.",
        reply_markup=user_main_menu(),
    )
    await callback.answer()
