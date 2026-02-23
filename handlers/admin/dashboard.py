"""
handlers/admin/dashboard.py - Unified Admin Dashboard.
Bot sozlamalari va adminlarni boshqarish inlineda.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from models.admin import AdminModel
from models.settings import SettingsModel
from models.user import UserModel
from keyboards.inline import (
    admin_dashboard_keyboard,
    admin_settings_keyboard,
    admin_manage_keyboard,
    admin_action_keyboard
)
from keyboards.reply import cancel_keyboard, admin_main_menu
from loader import bot
from filters.admin import is_admin


logger = logging.getLogger(__name__)
router = Router(name="admin_dashboard")

class DashboardStates(StatesGroup):
    waiting_setting_value = State()
    waiting_admin_id = State()

@router.message(F.text == "❌ Bekor qilish", F.state.any())
@router.message(F.text == "❌ Bekor qilish")
async def global_cancel_handler(message: Message, state: FSMContext) -> None:

    """Istalgan holatda amalni bekor qilish."""
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer(
            "❌ <b>Amal bekor qilindi.</b>", 
            reply_markup=admin_main_menu()
        )
    else:
        # Agar holat bo'lmasa ham asosiy menyuni ko'rsatamiz
        await message.answer(
            "<b>Asosiy admin menyusi:</b>", 
            reply_markup=admin_main_menu()
        )




@router.message(F.text == "⚙️ Dashbord", is_admin)

@router.callback_query(F.data == "admin_dashboard")
async def show_dashboard(event: Message | CallbackQuery, state: FSMContext) -> None:
    """Asosiy admin paneli."""
    await state.clear()
    text = (
        "<b>🛠 Admin Dashbord</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Botni boshqarish va sozlash uchun quyidagi bo'limlardan birini tanlang:"
    )
    kb = admin_dashboard_keyboard()
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)
        await event.answer()

# --- BOT SOZLAMALARI ---

@router.callback_query(F.data == "admin_settings", is_admin)
async def dashboard_settings(callback: CallbackQuery) -> None:
    settings = await SettingsModel.get_all()
    support = settings.get("support_link", "Tuzatilmagan")
    news = settings.get("news_channel", "Tuzatilmagan")
    maintenance = settings.get("maintenance_mode", "OFF")
    
    text = (
        "<b>⚙️ Bot Sozlamalari</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🙋‍♂️ <b>Support:</b> {support}\n"
        f"📢 <b>Kanal:</b> {news}\n"
        f"🛠 <b>Maintenance:</b> {maintenance}\n"
    )
    await callback.message.edit_text(text, reply_markup=admin_settings_keyboard(maintenance))
    await callback.answer()

@router.callback_query(F.data == "toggle_maintenance", is_admin)
async def toggle_maintenance_handler(callback: CallbackQuery) -> None:
    val = await SettingsModel.get("maintenance_mode", "OFF")
    new_val = "ON" if val == "OFF" else "OFF"
    await SettingsModel.set("maintenance_mode", new_val)
    await dashboard_settings(callback)

@router.callback_query(F.data.startswith("set_setting:"), is_admin)
async def start_set_setting(callback: CallbackQuery, state: FSMContext) -> None:
    key = callback.data.split(":")[1]
    await state.update_data(setting_key=key)
    await state.set_state(DashboardStates.waiting_setting_value)
    
    if key == "support_link":
        prompt = "🙋‍♂️ <b>Support havolasini kiriting:</b>"
    elif key == "news_channel":
        prompt = "📢 <b>Kanal havolasini kiriting:</b>"
    elif key == "vip_card_number":
        prompt = "💳 <b>Yangi karta raqamini kiriting:</b>"
    elif key == "vip_card_name":
        prompt = "👤 <b>Karta egasini ism-familiyasini kiriting:</b>"
    else:
        prompt = "📝 <b>Qiymatni kiriting:</b>"
        
    await callback.message.edit_text(prompt, reply_markup=cancel_keyboard())
    await callback.answer()


@router.message(DashboardStates.waiting_setting_value)
async def process_setting_value(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    key = data["setting_key"]
    val = message.text.strip()
    
    await SettingsModel.set(key, val)
    await state.clear()
    
    await message.answer(f"✅ Yangilandi: <code>{val}</code>", reply_markup=admin_main_menu())
    # Qayta dashbordga yoki sozlamalarga yo'naltirish (biz yangi xabar yubordik, chunki reply_keyboard ishlatdik)
    await show_dashboard(message, state)

# --- ADMINLAR BOSHQARUVI ---

@router.callback_query(F.data == "admin_admins", is_admin)
async def dashboard_admins(callback: CallbackQuery) -> None:
    admins = await AdminModel.get_all()
    text = (
        "<b>👥 Adminlar Boshqaruvi</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Mavjud adminlar ro'yxati:"
    )
    await callback.message.edit_text(text, reply_markup=admin_manage_keyboard(admins))
    await callback.answer()

@router.callback_query(F.data.startswith("view_admin:"), is_admin)
async def view_admin_handler(callback: CallbackQuery) -> None:
    admin_id = int(callback.data.split(":")[1])
    # Dastlabki adminlarni o'chirib bo'lmaydi (configdagilar)
    from config import ADMIN_IDS
    if admin_id in ADMIN_IDS:
        await callback.answer("⚠️ Bu asosiy admin, uni o'chirib bo'lmaydi!", show_alert=True)
        return
        
    text = f"👤 <b>Admin ID:</b> <code>{admin_id}</code>\n\nAmalni tanlang:"
    await callback.message.edit_text(text, reply_markup=admin_action_keyboard(admin_id))
    await callback.answer()

@router.callback_query(F.data.startswith("delete_admin:"), is_admin)
async def delete_admin_dashboard(callback: CallbackQuery) -> None:
    admin_id = int(callback.data.split(":")[1])
    success = await AdminModel.remove_admin(admin_id)
    if success:
        await callback.answer("✅ Admin muvaffaqiyatli o'chirildi.", show_alert=True)
    else:
        await callback.answer("❌ Xatolik: Adminni o'chirib bo'lmadi.", show_alert=True)
    await dashboard_admins(callback)


@router.callback_query(F.data == "add_new_admin", is_admin)
async def add_admin_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DashboardStates.waiting_admin_id)
    await callback.message.edit_text(
        "➕ <b>Yangi admin qo'shish</b>\n\n"
        "Foydalanuvchi ID raqamini kiriting yoki uning xabarini bu yerga forward qiling:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()

@router.message(DashboardStates.waiting_admin_id)
async def process_add_admin(message: Message, state: FSMContext) -> None:
    tg_id = None
    full_name = "Nomalum"
    
    # 1. Forward qilingan xabarni tekshirish (Yangi aiogram 3.x/Telegram API uslubi)
    if message.forward_origin:
        origin = message.forward_origin
        if hasattr(origin, 'sender_user'):
            tg_id = origin.sender_user.id
            full_name = origin.sender_user.full_name
        elif hasattr(origin, 'sender_chat'):
            tg_id = origin.sender_chat.id
            full_name = origin.sender_chat.title
        else:
            # Privacy settings tufayli ID yopiq bo'lishi mumkin
            await message.reply(
                "❌ <b>Xatolik!</b>\n\n"
                "Ushbu foydalanuvchining maxfiylik sozlamalari ID raqamini olishga ruxsat bermaydi. "
                "Iltimos, uning ID raqamini qo'lda kiriting."
            )
            return

    # 2. Text orqali ID kiritilganini tekshirish
    elif message.text and message.text.isdigit():
        tg_id = int(message.text)
        
    if not tg_id:
        await message.reply("❌ Noto'g'ri ID. Iltimos raqam kiriting yoki xabar forward qiling.")
        return

        
    success = await AdminModel.add_admin(tg_id, full_name)
    await state.clear()
    
    if success:
        # Yangi adminni ham is_admin deb tanishimiz kerak (bazada borligi uchun)
        await message.reply(
            f"✅ <b>Yangi admin tayinlandi!</b>\n\n"
            f"👤 <b>Ism:</b> {full_name}\n"
            f"🆔 <b>ID:</b> <code>{tg_id}</code>\n\n"
            "Endi ushbu foydalanuvchi barcha admin buyruqlaridan foydalana oladi.",
            reply_markup=admin_main_menu()
        )
    else:
        await message.reply(
            "❌ <b>Xatolik!</b>\n\n"
            "Ushbu foydalanuvchi allaqachon admindir yoki bazada texnik xatolik yuz berdi. "
            "Iltimos, loglarni tekshiring.", 
            reply_markup=admin_main_menu()
        )

        
    await show_dashboard(message, state)



# --- STATISTIKA ---

@router.callback_query(F.data == "admin_stats", is_admin)
async def dashboard_stats(callback: CallbackQuery) -> None:
    # Bu yerda modellardan statistikani yig'amiz
    # Hozircha oddiy
    from models.anime import AnimeModel
    from models.episode import EpisodeModel
    
    user_count = await UserModel.get_count()
    anime_count = await AnimeModel.get_count()
    episode_count = await EpisodeModel.get_total_count()
    
    text = (
        "<b>📊 Bot Statistikasi</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Foydalanuvchilar:</b> {user_count}\n"
        f"🎬 <b>Animelar:</b> {anime_count}\n"
        f"📁 <b>Qismlar:</b> {episode_count}\n"
    )
    await callback.message.edit_text(text, reply_markup=admin_dashboard_keyboard())
    await callback.answer()
