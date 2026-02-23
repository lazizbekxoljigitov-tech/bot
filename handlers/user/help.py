import logging
from aiogram import Router, F
from aiogram.types import Message
from models.settings import SettingsModel
from utils.images import IMAGES
from loader import bot

logger = logging.getLogger(__name__)
router = Router(name="user_help")


@router.message(F.text == "❓ Yordam")
@router.message(F.text == "/help")
async def cmd_help(message: Message) -> None:
    """Yordam xabarini ko'rsatish."""
    support = await SettingsModel.get("support_link", "@AdminUsername")
    bot_info = await bot.get_me()
    
    help_text = (
        "<b>❓ Yordam — Botdan foydalanish bo'yicha qo'llanma</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔍 <b>Anime qidirish</b> — Nomi, kodi yoki janri bo'yicha animelarni topishingiz mumkin.\n\n"
        "📺 <b>Ko'rish</b> — Anime sahifasiga o'tib, 'Tomosha qilish' tugmasini bosing va istalgan qismni tanlang.\n\n"
        "⭐️ <b>Sevimlilar</b> — O'zingizga yoqqan animelarni saqlab qo'ying va ularga tezda kiring.\n\n"
        "🎬 <b>Shorts</b> — Qisqa va qiziqarli lavhalarni tomosha qiling.\n\n"
        "💎 <b>VIP</b> — VIP maqomga ega bo'ling va eng yangi animelarni birinchilardan bo'lib, cheklovlarsiz tomosha qiling.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📩 <b>Savol va takliflar:</b> {support}\n"
        f"🤖 <b>Botimiz:</b> @{bot_info.username}"
    )
    from services.media_service import MediaService
    
    try:
        await MediaService.send_photo(
            event=message,
            photo=IMAGES["HELP"],
            caption=help_text,
            context_info="Yordam bo'limi"
        )
    except Exception:
        # MediaService already alerts admin on failure, but we want to ensure 
        # the user at least gets the text if the photo fails completely.
        await message.answer(help_text)

