"""
services/vip_service.py - VIP bilan bog'liq biznes logika.
Karta raqami plan ichidan olinadi.
"""

from datetime import datetime, timedelta
from models.user import UserModel
from models.vip import VipModel


class VipService:
    """VIP bilan bog'liq biznes logika xizmati."""

    @staticmethod
    async def activate_vip(telegram_id: int, plan_id: int) -> str:
        """Foydalanuvchiga VIP maqomini berish."""
        plan = await VipModel.get_plan(plan_id)
        if not plan:
            return "VIP reja topilmadi."
        expire_date = datetime.now() + timedelta(days=plan["duration_days"])
        expire_str = expire_date.strftime("%Y-%m-%d %H:%M:%S")
        await UserModel.set_vip(telegram_id, expire_str)
        return (
            f"\u2714 <b>VIP faollashtirildi!</b>\n\n"
            f"\u25B8 Reja: {plan['name']}\n"
            f"\u25B8 Muddat: {plan['duration_days']} kun\n"
            f"\u25B8 Tugash sanasi: {expire_str}\n"
        )

    @staticmethod
    async def get_plans_text(anime_title: str | None = None) -> str:
        """Barcha VIP rejalarning matnli ro'yxatini tayyorlash."""
        plans = await VipModel.get_all_plans()
        if not plans:
            return "\u25C6 Hozircha VIP rejalar mavjud emas."
        
        header = f"<b>\u25C6 {anime_title} | VIP</b>\n" if anime_title else "<b>\u25C6 VIP Rejalar</b>\n"
        
        text = (
            header +
            "━━━━━━━━━━━━━━━━━━\n\n"
            "✨ VIP i'mtiyozlariga ega bo'lish uchun quyidagi rejalardan birini tanlang:\n\n"
            "<i>(Batafsil ma'lumot tugmalarda ko'rsatilgan)</i>"
        )
        return text

    @staticmethod
    async def get_payment_text(plan_id: int) -> str:
        """To'lov ma'lumotlarini tayyorlash - karta raqami SettingsModel dan olinadi."""
        from models.settings import SettingsModel
        plan = await VipModel.get_plan(plan_id)
        if not plan:
            return "Reja topilmadi."
        
        # Karta raqami va egasini olish
        card_num = await SettingsModel.get("vip_card_number")
        card_name = await SettingsModel.get("vip_card_name")
        
        if not card_num:
            card_num = plan.get("card_number", "---") or "---"
        if not card_name:
            card_name = "Nomalum"

        return (
            f"<b>📋 VIP QO'LLANMA: To'lov</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"1️⃣ <b>To'lovni amalga oshiring:</b>\n"
            f"▸ <b>Miqdor:</b> <code>{plan['price']}</code> so'm\n"
            f"▸ <b>Reja:</b> {plan['name']} ({plan['duration_days']} kun)\n\n"
            f"💳 <b>REKVIZITLAR:</b>\n"
            f"▸ <b>Karta raqami:</b> <code>{card_num}</code>\n"
            f"▸ <b>Karta egasi:</b> <code>{card_name}</code>\n\n"
            f"2️⃣ <b>Screenshot yuboring:</b>\n"
            f"▸ To'lovni amalga oshirgach, chekni (screenshot) rasm sifatida shu yerga yuboring.\n\n"
            f"3️⃣ <b>Kuting:</b>\n"
            f"▸ Admin 15-30 daqiqa ichida to'lovni tekshiradi va VIP'ni faollashtiradi.\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"☝️ <i>Muvaffaqiyatli to'lovdan so'ng xabarni kuting!</i>"
        )
