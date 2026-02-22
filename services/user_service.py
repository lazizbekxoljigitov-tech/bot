"""
services/user_service.py - Foydalanuvchi profili va VIP xizmatlari.
Premium dizayn va chiroyli formatlash.
"""

from datetime import datetime
from models.user import UserModel


class UserService:
    """Foydalanuvchi ma'lumotlarini boshqarish va formatlash."""

    @staticmethod
    async def get_profile_text(telegram_id: int) -> str:
        """Foydalanuvchi profili ma'lumotlarini formatlash."""
        user = await UserModel.get_by_telegram_id(telegram_id)
        if not user:
            return "❌ Foydalanuvchi topilmadi."

        vip_status = "💎 VIP" if user["is_vip"] else "👤 Oddiy a'zo"
        vip_expire = user["vip_expire_date"] if user["is_vip"] else "---"
        
        # Ro'yxatdan o'tgan sana
        joined = user.get("joined_date", "---")

        text = (
            f"<b>👤 Mening Profilim</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"📎 <b>Ism:</b> {user['full_name']}\n"
            f"🆔 <b>ID:</b> <code>{user['telegram_id']}</code>\n"
            f"💎 <b>Maqom:</b> {vip_status}\n"
            f"⏳ <b>VIP tugash muddati:</b>\n   <code>{vip_expire}</code>\n"
            f"📅 <b>A'zo bo'lgan sana:</b>\n   <code>{joined}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🚀 <i>Anime olamida maroqli vaqt o'tkazing!</i>"
        )
        return text

    @staticmethod
    async def is_vip_active(telegram_id: int) -> bool:
        """VIP holati hali ham faolligini tekshirish."""
        user = await UserModel.get_by_telegram_id(telegram_id)
        if not user or not user["is_vip"]:
            return False

        if not user["vip_expire_date"]:
            return False

        try:
            expire_date = datetime.strptime(
                user["vip_expire_date"], "%Y-%m-%d %H:%M:%S"
            )
            return datetime.now() < expire_date
        except (ValueError, TypeError):
            return False

    @staticmethod
    async def check_and_expire_vip(telegram_id: int) -> bool:
        """VIP muddati tugagan bo'lsa, uni bekor qilish."""
        user = await UserModel.get_by_telegram_id(telegram_id)
        if not user or not user["is_vip"]:
            return False

        if not await UserService.is_vip_active(telegram_id):
            await UserModel.remove_vip(telegram_id)
            return True
        return False
