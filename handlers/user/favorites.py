import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from models.user import UserModel
from models.favorites import FavoritesModel
from utils.images import IMAGES
from keyboards.inline import favorites_keyboard, anime_view_keyboard

logger = logging.getLogger(__name__)
router = Router(name="user_favorites")


@router.message(F.text == "⭐️ Sevimlilar")
async def show_favorites(message: Message) -> None:
    """Foydalanuvchi sevimlilarini ro'yxatini ko'rsatish."""
    user = await UserModel.get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("❌ Avval /start buyrug'ini bosing.")
        return

    favs = await FavoritesModel.get_by_user(user["id"])
    
    if not favs:
        text = (
            "<b>⭐️ Sevimlilar</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Sizda hali sevimlilar yo'q. 🔍 Anime qidirish bo'limidan animelarni toping va sevimlilarga qo'shing!"
        )
        try:
            await message.answer_photo(
                photo=IMAGES["SEARCH"],
                caption=text,
                reply_markup=favorites_keyboard([])
            )
        except Exception as e:
            logger.error(f"Error sending empty favorites photo: {e}")
            await message.answer(text, reply_markup=favorites_keyboard([]))
        return

    text = (
        "<b>⭐️ Mening Sevimlilarim</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Siz tomondan saqlangan animelar:"
    )
    await message.answer(text, reply_markup=favorites_keyboard(favs))


@router.callback_query(F.data.startswith("fav:"))
async def add_favorite_callback(callback: CallbackQuery) -> None:
    """Anime sahifasidan sevimlilarga qo'shish."""
    anime_id = int(callback.data.split(":")[1])
    user = await UserModel.get_by_telegram_id(callback.from_user.id)
    
    if user:
        added = await FavoritesModel.add(user["id"], anime_id)
        if added:
            await callback.answer("✅ Sevimlilarga qo'shildi!", show_alert=False)
            # Klaviatura holatini yangilash
            await callback.message.edit_reply_markup(
                reply_markup=anime_view_keyboard(anime_id, is_favorite=True)
            )
        else:
            await callback.answer("ℹ️ Allaqachon qo'shilgan.")
    else:
        await callback.answer("❌ Xatolik!")


@router.callback_query(F.data.startswith("unfav:"))
async def remove_favorite_callback(callback: CallbackQuery) -> None:
    """Anime sahifasidan sevimlilardan chiqarish."""
    anime_id = int(callback.data.split(":")[1])
    user = await UserModel.get_by_telegram_id(callback.from_user.id)
    
    if user:
        await FavoritesModel.remove(user["id"], anime_id)
        await callback.answer("🗑 Sevimlilardan chiqarildi!", show_alert=False)
        # Klaviatura holatini yangilash
        await callback.message.edit_reply_markup(
            reply_markup=anime_view_keyboard(anime_id, is_favorite=False)
        )
    else:
        await callback.answer("❌ Xatolik!")
