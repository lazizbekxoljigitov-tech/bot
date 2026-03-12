import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from states.channel import AddChannelStates
from filters.admin import is_admin
from models.channel import ChannelModel
from keyboards.reply import cancel_keyboard, admin_main_menu
from keyboards.inline import admin_channels_keyboard

logger = logging.getLogger(__name__)
router = Router(name="admin_subscription")


@router.message(F.text == "🚫 Majburiy obuna", is_admin)
async def subscription_menu(message: Message) -> None:
    """Majburiy obuna menyusi - kanallar ro'yxati."""
    channels = await ChannelModel.get_all()
    text = "<b>🚫 Majburiy obuna sozlamalari</b>\n━━━━━━━━━━━━━━━━━━\n\n"
    
    if channels:
        for i, ch in enumerate(channels, 1):
            text += f"{i}. <b>{ch['channel_name']}</b>\n"
            text += f"└ <code>{ch['channel_id']}</code>\n"
            text += f"└ <a href='{ch['channel_link']}'>Havola</a>\n\n"
    else:
        text += "Hozircha majburiy obuna kanallari yo'q.\n"
    
    text += "━━━━━━━━━━━━━━━━━━\n"
    text += "• Yangi kanal qo'shish uchun: /add_channel\n"
    text += "• Kanalni o'chirish uchun: /remove_channel"
    
    await message.answer(text, disable_web_page_preview=True)


@router.message(F.text == "/add_channel", is_admin)
async def add_channel_start(message: Message, state: FSMContext) -> None:
    """Kanal qo'shishni boshlash - nom so'rash."""
    await state.set_state(AddChannelStates.channel_name)
    await message.answer(
        "<b>📢 Yangi kanal qo'shish</b>\n\nKanal nomini kiriting (tugmada ko'rinadigan nom):",
        reply_markup=cancel_keyboard()
    )


@router.message(AddChannelStates.channel_name, is_admin)
async def add_channel_name(message: Message, state: FSMContext) -> None:
    """Kanal nomini saqlash va havolani so'rash."""
    await state.update_data(channel_name=message.text.strip())
    await state.set_state(AddChannelStates.channel_link)
    await message.answer(
        "<b>🔗 Kanal havolasini yuboring</b>\n\n"
        "Masalan: <code>https://t.me/kanal_nomi</code> yoki <code>@kanal_nomi</code>\n\n"
        "<i>Eslatma: Bot ushbu kanalda ADMIN bo'lishi shart!</i>",
        reply_markup=cancel_keyboard()
    )


@router.message(AddChannelStates.channel_link, is_admin)
async def add_channel_link(message: Message, state: FSMContext) -> None:
    """Kanalni tekshirish va saqlash."""
    link = message.text.strip()
    data = await state.get_data()
    name = data['channel_name']
    
    # Havolani ID ga aylantirish (oddiy @username bo'lsa)
    chat_id = link
    if "t.me/" in link:
        chat_id = "@" + link.split("t.me/")[-1].replace("/", "")
    
    try:
        # Kanal ma'lumotlarini olishga harakat qilamiz
        chat = await message.bot.get_chat(chat_id)
        
        # Numeric ID ni olamiz
        numeric_id = str(chat.id)
        
        # Bazaga qo'shish
        await ChannelModel.add(
            channel_id=numeric_id,
            channel_name=name,
            channel_link=link if "http" in link else f"https://t.me/{chat.username}"
        )
        
        await state.clear()
        await message.answer(
            f"✅ <b>Kanal muvaffaqiyatli qo'shildi!</b>\n\n"
            f"▸ Nomi: {name}\n"
            f"▸ ID: <code>{numeric_id}</code>\n"
            f"▸ Username: @{chat.username}",
            reply_markup=admin_main_menu()
        )
        
    except TelegramBadRequest as e:
        await message.answer(
            f"❌ <b>Xatolik yuz berdi!</b>\n\n"
            f"Bot ushbu kanalni topa olmadi yoki bot kanalda admin emas.\n"
            f"Iltimos, botni kanalga admin qiling va qayta urunib ko'ring.\n\n"
            f"Xato: <code>{str(e)}</code>",
            reply_markup=admin_main_menu()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Add channel error: {e}")
        await message.answer(f"❌ <b>Kutilmagan xatolik:</b> {e}", reply_markup=admin_main_menu())
        await state.clear()


@router.message(F.text == "/remove_channel", is_admin)
async def remove_channel_start(message: Message) -> None:
    """Kanalni o'chirish - inline ro'yxat ko'rsatish."""
    channels = await ChannelModel.get_all()
    if not channels:
        await message.answer("O'chirish uchun kanallar yo'q.")
        return
        
    await message.answer(
        "<b>🗑 O'chirish uchun kanalni tanlang:</b>",
        reply_markup=admin_channels_keyboard(channels)
    )


@router.callback_query(F.data.startswith("del_channel:"), is_admin)
async def remove_channel_callback(callback: CallbackQuery) -> None:
    """Kanalni o'chirish callbacki."""
    channel_id = callback.data.split(":")[1]
    
    try:
        await ChannelModel.remove(channel_id)
        await callback.message.edit_text("✅ <b>Kanal majburiy obunadan olib tashlandi.</b>")
    except Exception as e:
        logger.error(f"Remove channel error: {e}")
        await callback.answer(f"❌ Xatolik: {e}", show_alert=True)
    
    await callback.answer()


