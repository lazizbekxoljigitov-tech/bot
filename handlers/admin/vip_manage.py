"""
handlers/admin/vip_manage.py - VIP boshqarish handlerlari (admin).
VIP plan yaratish (karta raqami bilan) va to'lovlarni tasdiqlash.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from states.vip import VipPlanStates
from models.vip import VipModel
from models.admin import AdminModel
from services.vip_service import VipService
from keyboards.reply import cancel_keyboard, admin_main_menu
from loader import bot

logger = logging.getLogger(__name__)
router = Router(name="admin_vip_manage")

async def is_admin(message: Message) -> bool:
    return await AdminModel.is_admin(message.from_user.id)

@router.message(F.text == "💎 VIP boshqarish", is_admin)
async def vip_manage_menu(message: Message, state: FSMContext) -> None:
    """VIP boshqarish menyusi."""
    plans = await VipModel.get_all_plans()
    text = "<b>💎 VIP Boshqarish</b>\n━━━━━━━━━━━━━━━━━━\n\n"
    if plans:
        text += "<b>Mavjud rejalar:</b>\n"
        for p in plans:
            card = p.get('card_number', '---') or '---'
            text += (
                f"\u25B8 {p['name']} - {p['price']} so'm "
                f"({p['duration_days']} kun) [ID: {p['id']}]\n"
                f"   Karta: {card}\n"
            )
    else:
        text += "Hozircha rejalar mavjud emas.\n"
    text += (
        "\n<b>Amallar:</b>\n"
        "\u25B8 /create_plan - Yangi plan yaratish\n"
        "\u25B8 /delete_plan [ID] - Plan o'chirish"
    )
    await message.answer(text)

@router.message(F.text == "/create_plan", is_admin)
async def create_plan_start(message: Message, state: FSMContext) -> None:
    await state.set_state(VipPlanStates.name)
    await message.answer(
        "<b>\u25C6 Yangi VIP plan yaratish</b>\n\n"
        "\u25B8 Plan nomini kiriting (masalan: 1 oylik VIP):",
        reply_markup=cancel_keyboard(),
    )

@router.message(VipPlanStates.name, is_admin)
async def create_plan_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(VipPlanStates.price)
    await message.answer("\u25B8 Narxni kiriting (so'mda, raqam):")

@router.message(VipPlanStates.price, is_admin)
async def create_plan_price(message: Message, state: FSMContext) -> None:
    try:
        price = int(message.text.strip())
        if price < 0:
            raise ValueError
    except ValueError:
        await message.answer("\u2716 To'g'ri raqam kiriting:")
        return
    await state.update_data(price=price)
    await state.set_state(VipPlanStates.duration_days)
    await message.answer("\u25B8 Muddat (kunlarda, masalan: 30):")

@router.message(VipPlanStates.duration_days, is_admin)
async def create_plan_duration(message: Message, state: FSMContext) -> None:
    try:
        days = int(message.text.strip())
        if days < 1:
            raise ValueError
    except ValueError:
        await message.answer("\u2716 To'g'ri raqam kiriting:")
        return
    await state.update_data(duration_days=days)
    await state.set_state(VipPlanStates.card_number)
    await message.answer(
        "\u25B8 To'lov karta raqamini kiriting\n"
        "(masalan: <code>8600 1234 5678 9012</code>):"
    )

@router.message(VipPlanStates.card_number, is_admin)
async def create_plan_card(message: Message, state: FSMContext) -> None:
    """Karta raqamini qabul qilish va planni saqlash."""
    card = message.text.strip()
    data = await state.get_data()
    await state.clear()

    plan_id = await VipModel.create_plan(
        name=data["name"],
        price=data["price"],
        duration_days=data["duration_days"],
        card_number=card,
    )

    await message.answer(
        f"\u2714 <b>VIP plan yaratildi!</b>\n\n"
        f"\u25B8 Nom: {data['name']}\n"
        f"\u25B8 Narx: {data['price']} so'm\n"
        f"\u25B8 Muddat: {data['duration_days']} kun\n"
        f"\u25B8 Karta: {card}\n"
        f"\u25B8 ID: {plan_id}",
        reply_markup=admin_main_menu(),
    )

@router.message(F.text.startswith("/delete_plan"), is_admin)
async def delete_plan(message: Message) -> None:
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("\u25B8 Foydalanish: /delete_plan [ID]")
        return
    try:
        plan_id = int(parts[1])
    except ValueError:
        await message.answer("\u2716 To'g'ri ID kiriting.")
        return
    plan = await VipModel.get_plan(plan_id)
    if not plan:
        await message.answer("\u2716 Plan topilmadi.")
        return
    await VipModel.delete_plan(plan_id)
    await message.answer(f"\u2714 <b>\"{plan['name']}\"</b> plani o'chirildi!")

# ==============================================================
# VIP TO'LOVNI TASDIQLASH / RAD ETISH (CALLBACK)
# ==============================================================

@router.callback_query(F.data.startswith("vip_approve:"))
async def approve_vip_payment(callback: CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Ruxsat yo'q.")
        return
    parts = callback.data.split(":")
    user_tg_id = int(parts[1])
    plan_id = int(parts[2])
    result_text = await VipService.activate_vip(user_tg_id, plan_id)
    try:
        await bot.send_message(user_tg_id, result_text)
    except Exception as e:
        logger.error("VIP xabar: %s", str(e))
    await callback.message.edit_text(
        f"\u2714 VIP faollashtirildi!\nFoydalanuvchi: {user_tg_id}"
    )
    await callback.answer("\u2714 Tasdiqlandi!")

@router.callback_query(F.data.startswith("vip_reject:"))
async def reject_vip_payment(callback: CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Ruxsat yo'q.")
        return
    user_tg_id = int(callback.data.split(":")[1])
    try:
        await bot.send_message(
            user_tg_id,
            "\u2716 <b>VIP so'rovingiz rad etildi.</b>\n\n"
            "To'g'ri screenshot yuboring.",
        )
    except Exception as e:
        logger.error("Rad xabar: %s", str(e))
    await callback.message.edit_text(
        f"\u2716 VIP rad etildi.\nFoydalanuvchi: {user_tg_id}"
    )
    await callback.answer("\u2716 Rad etildi!")
