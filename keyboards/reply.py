"""
keyboards/reply.py - Asosiy menyu va matnli tugmalar (Reply Keyboards).
Unicode va Emojilar bilan boyitilgan premium dizayn.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_IDS


def user_main_menu() -> ReplyKeyboardMarkup:
    """Foydalanuvchi uchun asosiy menyu."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="\u2302 Bosh sahifa"),
                KeyboardButton(text="🔍 Anime qidirish"),
            ],
            [
                KeyboardButton(text="🎬 Shorts"),
                KeyboardButton(text="⭐️ Sevimlilar"),
            ],
            [
                KeyboardButton(text="💎 VIP"),
                KeyboardButton(text="🔥 Top Anime"),
            ],
            [
                KeyboardButton(text="👤 Profilim"),
                KeyboardButton(text="❓ Yordam"),
            ],
        ],
        resize_keyboard=True,
    )


def admin_main_menu() -> ReplyKeyboardMarkup:
    """Adminlar uchun asosiy menyu (2-ustunli, mantiqiy guruhlangan)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            # ANIME BOSHQARUVI
            [
                KeyboardButton(text="➕ Anime qo'shish"),
                KeyboardButton(text="📝 Anime tahrirlash"),
            ],
            [
                KeyboardButton(text="❌ Anime o'chirish"),
                KeyboardButton(text="🎬 Shorts qo'shish"),
            ],
            # QISMLAR BOSHQARUVI
            [
                KeyboardButton(text="➕ Qism qo'shish"),
                KeyboardButton(text="📝 Qism tahrirlash"),
            ],
            [
                KeyboardButton(text="❌ Qism o'chirish"),
                KeyboardButton(text="📢 Kanalga post"),
            ],
            # VIP VA BROADCAST
            [
                KeyboardButton(text="💎 VIP boshqarish"),
                KeyboardButton(text="📤 Xabar yuborish"),
            ],
            # STATISTIKA VA SOZLAMALAR
            [
                KeyboardButton(text="📊 Statistika"),
                KeyboardButton(text="🚫 Majburiy obuna"),
            ],
            [
                KeyboardButton(text="🛠 Boshqaruv"),
                KeyboardButton(text="⬅️ Foydalanuvchi paneli"),
            ],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Amalni bekor qilish tugmasi."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
    )


def skip_keyboard() -> ReplyKeyboardMarkup:
    """O'tkazib yuborish tugmasi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏩ O'tkazib yuborish")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )


def vip_choice_keyboard() -> ReplyKeyboardMarkup:
    """VIP holatini tanlash (admin uchun)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Ha (VIP)"),
                KeyboardButton(text="Yo'q (Oddiy)"),
            ],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )


def confirm_keyboard() -> ReplyKeyboardMarkup:
    """Tasdiqlash tugmalari."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Tasdiqlash"),
                KeyboardButton(text="❌ Bekor qilish"),
            ]
        ],
        resize_keyboard=True,
    )


def search_menu() -> ReplyKeyboardMarkup:
    """Qidiruv turlarini tanlash menyusi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Nomi bo'yicha"),
                KeyboardButton(text="🔢 Kod bo'yicha"),
            ],
            [
                KeyboardButton(text="🎭 Janr bo'yicha"),
                KeyboardButton(text="💎 VIP animelar"),
            ],
            [
                KeyboardButton(text="🌟 Top animelar"),
                KeyboardButton(text="🆕 Yangi animelar"),
            ],
            [KeyboardButton(text="⬅️ Orqaga")],
        ],
        resize_keyboard=True,
    )


def channel_post_menu() -> ReplyKeyboardMarkup:
    """Kanalga post yuborish formatlari."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🖼 Katta post"),
                KeyboardButton(text="📄 Kichik post"),
            ],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )
