"""
handlers/vip/plans.py - VIP rejalar va to'lov handleri.
Karta raqami plan ichidan olinadi.
"""

import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from states.vip import VipPaymentStates
from models.vip import VipModel
from models.user import UserModel
from services.vip_service import VipService
from services.user_service import UserService
from utils.images import IMAGES
from keyboards.inline import vip_plans_keyboard, vip_payment_keyboard, vip_admin_approve_keyboard, vip_details_keyboard
from loader import bot

logger = logging.getLogger(__name__)
router = Router(name="vip_plans")

@router.message(F.text == "💎 VIP")
async def show_vip_plans(message: Message, state: FSMContext) -> None:
    """VIP rejalarni ko'rsatish."""
    data = await state.get_data()
    anime_title = data.get("context_anime_title")
    
    is_vip = await UserService.is_vip_active(message.from_user.id)
    plans = await VipModel.get_all_plans()
    text = await VipService.get_plans_text(anime_title)
    kb = vip_plans_keyboard(plans, is_vip=is_vip, anime_title=anime_title) if plans else None
    
    try:
        await message.answer_photo(
            photo=IMAGES["VIP"],
            caption=text,
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Error sending VIP photo: {e}")
        await message.answer(text, reply_markup=kb)

@router.callback_query(F.data == "vip_plans_back")
async def vip_plans_back_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """VIP rejalar ro'yxatiga qaytish."""
    data = await state.get_data()
    anime_title = data.get("context_anime_title")
    
    is_vip = await UserService.is_vip_active(callback.from_user.id)
    plans = await VipModel.get_all_plans()
    text = await VipService.get_plans_text(anime_title)
    kb = vip_plans_keyboard(plans, is_vip=is_vip, anime_title=anime_title) if plans else None
    
    try:
        await callback.message.edit_caption(caption=text, reply_markup=kb)
    except Exception:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=IMAGES["VIP"],
            caption=text,
            reply_markup=kb
        )
    await callback.answer()

@router.callback_query(F.data.startswith("vip_details:"))
async def view_vip_details(callback: CallbackQuery) -> None:
    """Reja tafsilotlarini ko'rsatish."""
    plan_id = int(callback.data.split(":")[1])
    plan = await VipModel.get_plan(plan_id)
    if not plan:
        await callback.answer("Reja topilmadi.", show_alert=True)
        return
        
    text = (
        f"<b>💎 {plan['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 <b>Narxi:</b> {plan['price']} so'm\n"
        f"⏳ <b>Muddati:</b> {plan['duration_days']} kun\n\n"
        "To'lovni amalga oshirish va yo'riqnomani ko'rish uchun yuqoridagi <b>bilan narx/kun</b> tugmasini bosing:"
    )
    
    try:
        await callback.message.edit_caption(
            caption=text, 
            reply_markup=vip_details_keyboard(plan)
        )
    except Exception:
        await callback.message.answer(text, reply_markup=vip_details_keyboard(plan))
    await callback.answer()

@router.callback_query(F.data.startswith("vip_plan:"))
async def select_vip_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """VIP reja tanlash - karta raqami plan dan ko'rsatiladi."""
    plan_id = int(callback.data.split(":")[1])
    text = await VipService.get_payment_text(plan_id)
    await state.set_state(VipPaymentStates.waiting_screenshot)
    await state.update_data(plan_id=plan_id)
    
    # Rasm bo'lgani uchun edit_caption ishlatiladi
    try:
        await callback.message.edit_caption(
            caption=text, reply_markup=vip_payment_keyboard(plan_id)
        )
    except Exception:
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer(
            text, reply_markup=vip_payment_keyboard(plan_id)
        )
    await callback.answer("💳 To'lov ma'lumotlari yuborildi.")

@router.callback_query(F.data.startswith("vip_paid:"))
async def vip_paid_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    text = "\u25B8 To'lov screenshotini rasm sifatida yuboring:"
    try:
        await callback.message.edit_caption(caption=text)
    except Exception:
        await callback.message.answer(text)
    await callback.answer()

@router.message(VipPaymentStates.waiting_screenshot, F.photo)
async def vip_screenshot_received(message: Message, state: FSMContext) -> None:
    """Screenshot qabul qilish va adminlarga yuborish."""
    data = await state.get_data()
    await state.clear()
    plan_id = data.get("plan_id")
    context_anime = data.get("context_anime_title")
    plan = await VipModel.get_plan(plan_id) if plan_id else None
    user = message.from_user
    photo_id = message.photo[-1].file_id

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    anime_info = f"🎬 <b>Anime:</b> {context_anime}\n" if context_anime else ""
    text = (
        f"<b>📋 YANGI VIP ZAYAVKA</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Foydalanuvchi:</b> {user.full_name}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"🔗 <b>Username:</b> @{user.username or 'yoq'}\n\n"
        f"{anime_info}"
        f"💎 <b>Tanlangan reja:</b> {plan['name'] if plan else 'Nomalum'}\n"
        f"💰 <b>To'lov miqdori:</b> {plan['price'] if plan else '---'} so'm\n"
        f"⏰ <b>Yuborilgan vaqt:</b> {now}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                chat_id=admin_id, 
                photo=photo_id, 
                caption=text,
                reply_markup=vip_admin_approve_keyboard(user.id, plan_id),
            )
        except Exception as e:
            logger.error("Admin ga yuborishda xatolik: %s", str(e))

    await message.answer(
        "✅ <b>Zayavkangiz adminga yuborildi!</b>\n\n"
        "⏳ Admin to'lovni tekshirib, 15-30 daqiqa ichida VIP statusni faollashtiradi.\n"
        "Xabarni kuting! 🚀"
    )

@router.message(VipPaymentStates.waiting_screenshot)
async def vip_screenshot_invalid(message: Message) -> None:
    await message.answer(
        "⚠️ <b>Iltimos, to'lov chekini rasm holatida yuboring!</b>\n\n"
        "To'lovni amalga oshirgach, chekni (screenshot) rasm sifatida shu yerga yuborishingiz kerak. "
        "Matn yoki fayl qabul qilinmaydi."
    )
