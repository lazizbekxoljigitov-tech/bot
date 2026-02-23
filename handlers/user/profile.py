import logging
from aiogram import Router, F
from aiogram.types import Message
from services.user_service import UserService
from services.media_service import MediaService
from utils.images import IMAGES


logger = logging.getLogger(__name__)
router = Router(name="user_profile")


@router.message(F.text == "👤 Profilim")
@router.message(F.text == "/profile")
async def show_profile(message: Message) -> None:
    """Foydalanuvchi profilini ko'rsatish."""
    # VIP muddatini tekshirish va yangilash
    await UserService.check_and_expire_vip(message.from_user.id)
    
    # Profil matnini olish (emoji va formatlash service ichida)
    text = await UserService.get_profile_text(message.from_user.id)
    try:
        await MediaService.send_photo(
            event=message,
            photo=IMAGES["PROFILE"],
            caption=text,
            context_info="Profile Photo"
        )
    except Exception:
        await message.answer("❌ <b>Profilni yuklashda xatolik yuz berdi.</b>")

