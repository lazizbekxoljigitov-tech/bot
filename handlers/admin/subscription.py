"""
handlers/admin/subscription.py - Majburiy obuna boshqarish handleri (admin).
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from states.channel import AddChannelStates
from filters.admin import is_admin
from models.channel import ChannelModel

from models.admin import AdminModel
from keyboards.reply import cancel_keyboard, admin_main_menu

logger = logging.getLogger(__name__)
router = Router(name="admin_subscription")



@router.message(F.text == "🚫 Majburiy obuna", is_admin)
async def subscription_menu(message: Message) -> None:
    channels = await ChannelModel.get_all()
    text = "<b>🚫 Majburiy obuna</b>\n━━━━━━━━━━━━━━━━━━\n\n"
    if channels:
        for ch in channels:
            text += f"\u25B8 {ch['channel_id']} - {ch['channel_link']}\n"
    else:
        text += "Kanallar qo'shilmagan.\n"
    text += "\n/add_channel - Qo'shish\n/remove_channel [id] - O'chirish"
    await message.answer(text)

@router.message(F.text == "/add_channel", is_admin)
async def add_channel_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AddChannelStates.channel_id)
    await message.answer("Kanal ID kiriting:", reply_markup=cancel_keyboard())

@router.message(AddChannelStates.channel_id, is_admin)
async def add_channel_id(message: Message, state: FSMContext) -> None:
    await state.update_data(channel_id=message.text.strip())
    await state.set_state(AddChannelStates.channel_link)
    await message.answer("Kanal havolasini kiriting (e.g., https://t.me/kanal_link):")

@router.message(AddChannelStates.channel_link, is_admin)
async def add_channel_link(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    channel_id = data.get("channel_id")
    channel_link = message.text.strip()
    
    try:
        await ChannelModel.add(channel_id, channel_link)
        await state.clear()
        await message.answer(f"✅ <b>Kanal qo'shildi!</b>", reply_markup=admin_main_menu())
    except Exception as e:
        logger.error(f"Add channel error: {e}")
        await message.answer(f"❌ <b>Xatolik:</b> {e}", reply_markup=admin_main_menu())

@router.message(F.text.startswith("/remove_channel"), is_admin)
async def remove_channel_handler(message: Message) -> None:
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ Format: <code>/remove_channel [id]</code>")
        return
        
    try:
        success = await ChannelModel.remove(parts[1])
        if success:
            await message.answer(f"✅ <b>Kanal o'chirildi!</b>")
        else:
            await message.answer(f"❌ <b>Xatolik:</b> Kanal topilmadi.")
    except Exception as e:
        logger.error(f"Remove channel error: {e}")
        await message.answer(f"❌ <b>Xatolik:</b> {e}")

