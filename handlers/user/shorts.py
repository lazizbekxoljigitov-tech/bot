"""
handlers/user/shorts.py - Shorts videolarini ko'rish.
Emoji va premium dizayn bilan.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from models.shorts import ShortsModel
from models.user import UserModel
from keyboards.inline import shorts_keyboard

router = Router(name="user_shorts")


@router.message(F.text == "🎬 Shorts")
async def show_shorts_start(message: Message) -> None:
    """Birinchi short videoni ko'rsatish."""
    shorts = await ShortsModel.get_all(limit=50)
    if not shorts:
        await message.answer("🎬 <b>Hozircha shortslar mavjud emas.</b>")
        return

    first_short = shorts[0]
    total = len(shorts)
    
    # Ko'rishlar sonini oshirish (Unik)
    db_user = await UserModel.get_by_telegram_id(message.from_user.id)
    if db_user:
        await ShortsModel.increment_views(first_short["id"], db_user["id"])
    
    # Yangilangan ma'lumotni olish (views o'zgarishi uchun)
    updated_short = await ShortsModel.get_by_id(first_short["id"])
    
    text = (
        f"<b>🎬 Shorts | {first_short['anime_title']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"👁 <b>Ko'rilgan:</b> {updated_short['views']}\n"
    )
    
    try:
        await message.answer_video(
            video=first_short["short_video_file_id"],
            caption=text,
            reply_markup=shorts_keyboard(first_short["id"], first_short["anime_id"], 0, total),
        )
    except Exception as e:
        logger.error(f"Shorts yuborishda xatolik: {e}")
        await message.answer(
            f"🎬 <b>Shorts yuklashda xatolik yuz berdi.</b>\n"
            f"Video fayl o'chirilgan yoki yaroqsiz bo'lishi mumkin.\n\n"
            f"ID: <code>{first_short['id']}</code>",
            reply_markup=shorts_keyboard(first_short["id"], first_short["anime_id"], 0, total),
        )


@router.callback_query(F.data.startswith("short_nav:"))
async def navigate_shorts(callback: CallbackQuery) -> None:
    """Shortslar o'rtasida navigatsiya."""
    index = int(callback.data.split(":")[1])
    shorts = await ShortsModel.get_all(limit=50)
    
    if not shorts or index >= len(shorts) or index < 0:
        await callback.answer("❌ Boshqa short yo'q.")
        return

    current = shorts[index]
    total = len(shorts)
    
    # Ko'rishlar sonini oshirish (Unik)
    db_user = await UserModel.get_by_telegram_id(callback.from_user.id)
    if db_user:
        await ShortsModel.increment_views(current["id"], db_user["id"])
    
    # Yangilangan ma'lumotni olish
    updated_short = await ShortsModel.get_by_id(current["id"])
    
    text = (
        f"<b>🎬 Shorts | {current['anime_title']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"👁 <b>Ko'rilgan:</b> {updated_short['views']}\n"
    )
    
    # Video o'zgargani uchun yangi xabar yuborish yaxshiroq (edit_media ba'zan sekin/xatoli)
    try:
        await callback.message.delete()
        await callback.message.answer_video(
            video=current["short_video_file_id"],
            caption=text,
            reply_markup=shorts_keyboard(current["id"], current["anime_id"], index, total),
        )
    except Exception as e:
        logger.error(f"Shorts navigatsiyasida xatolik: {e}")
        await callback.message.answer(
            f"❌ <b>Videoni yuklab bo'lmadi.</b>\n"
            f"Fayl topilmadi yoki o'chirilgan.",
            reply_markup=shorts_keyboard(current["id"], current["anime_id"], index, total),
        )
    await callback.answer()
