"""
handlers/admin/anime_crud.py - Anime CRUD handlerlari (admin).
Anime qo'shish, tahrirlash va o'chirish.
"""

import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from states.anime import AddAnimeStates, EditAnimeStates
from models.anime import AnimeModel
from models.admin import AdminModel
from keyboards.reply import cancel_keyboard, skip_keyboard, vip_choice_keyboard, admin_main_menu
from keyboards.inline import anime_view_keyboard, anime_select_keyboard, admin_fix_media_keyboard

from filters.admin import is_admin

logger = logging.getLogger(__name__)
router = Router(name="admin_anime_crud")


# ---- Faqat adminlar uchun filter ----



# ==============================================================
# ANIME QO'SHISH
# ==============================================================

@router.message(F.text == "➕ Anime qo'shish", is_admin)
async def add_anime_start(message: Message, state: FSMContext) -> None:
    """Anime qo'shish jarayonini boshlash."""
    await state.set_state(AddAnimeStates.title)
    await message.answer(
        "<b>➕ Yangi anime qo'shish</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "◈ Anime nomini kiriting:",
        reply_markup=cancel_keyboard(),
    )


@router.message(AddAnimeStates.title, is_admin)
async def add_anime_title(message: Message, state: FSMContext) -> None:
    """Anime nomi qabul qilish."""
    await state.update_data(title=message.text.strip())
    await state.set_state(AddAnimeStates.code)
    await message.answer(
        "◈ Anime kodini kiriting (unique, masalan: <code>naruto</code>):"
    )


@router.message(AddAnimeStates.code, is_admin)
async def add_anime_code(message: Message, state: FSMContext) -> None:
    """Anime kodi qabul qilish."""
    code = message.text.strip().lower()
    existing = await AnimeModel.get_by_code(code)
    if existing:
        await message.answer(
            f"\u2716 <b>\"{code}\"</b> kodi allaqachon mavjud. Boshqa kod kiriting:"
        )
        return
    await state.update_data(code=code)
    await state.set_state(AddAnimeStates.description)
    await message.answer(
        "◈ Anime tavsifini kiriting:",
        reply_markup=skip_keyboard(),
    )


@router.message(AddAnimeStates.description, is_admin)
async def add_anime_description(message: Message, state: FSMContext) -> None:
    """Anime tavsifi qabul qilish."""
    if message.text == "⏩ O'tkazib yuborish":
        await state.update_data(description="Tavsif kiritilmagan")
    else:
        await state.update_data(description=message.text.strip())
    await state.set_state(AddAnimeStates.genre)
    await message.answer(
        "◈ Janrni kiriting (masalan: Action, Romance, Fantasy):",
        reply_markup=skip_keyboard(),
    )


@router.message(AddAnimeStates.genre, is_admin)
async def add_anime_genre(message: Message, state: FSMContext) -> None:
    """Anime janri qabul qilish."""
    if message.text == "⏩ O'tkazib yuborish":
        await state.update_data(genre="Noma'lum")
    else:
        await state.update_data(genre=message.text.strip())
    await state.set_state(AddAnimeStates.season_count)
    await message.answer(
        "◈ Sezonlar sonini kiriting (raqam):",
        reply_markup=cancel_keyboard(),
    )


@router.message(AddAnimeStates.season_count, is_admin)
async def add_anime_season_count(message: Message, state: FSMContext) -> None:
    """Sezonlar soni qabul qilish."""
    try:
        count = int(message.text.strip())
        if count < 1:
            raise ValueError
    except ValueError:
        await message.answer("\u2716 Iltimos, to'g'ri raqam kiriting:")
        return
    await state.update_data(season_count=count)
    await state.set_state(AddAnimeStates.total_episodes)
    await message.answer("◈ Umumiy qismlar sonini kiriting (raqam):")


@router.message(AddAnimeStates.total_episodes, is_admin)
async def add_anime_total_episodes(message: Message, state: FSMContext) -> None:
    """Qismlar soni qabul qilish."""
    try:
        count = int(message.text.strip())
        if count < 0:
            raise ValueError
    except ValueError:
        await message.answer("\u2716 Iltimos, to'g'ri raqam kiriting:")
        return
    await state.update_data(total_episodes=count)
    await state.set_state(AddAnimeStates.status)
    await message.answer(
        "<b>\u25B8 Anime holatini kiriting:</b>\n"
        "(Masalan: <code>Tugallangan</code>, <code>Davom etmoqda</code>)",
        reply_markup=skip_keyboard(),
    )


@router.message(AddAnimeStates.status, is_admin)
async def add_anime_status(message: Message, state: FSMContext) -> None:
    """Anime holati qabul qilish."""
    if message.text == "⏩ O'tkazib yuborish":
        await state.update_data(status="Tugallangan")
    else:
        await state.update_data(status=message.text.strip())
    await state.set_state(AddAnimeStates.translator)
    await message.answer(
        "<b>\u25B8 Tarjimonni kiriting:</b>\n"
        "(Masalan: <code>AniBro</code>)",
        reply_markup=skip_keyboard(),
    )


@router.message(AddAnimeStates.translator, is_admin)
async def add_anime_translator(message: Message, state: FSMContext) -> None:
    """Tarjimon qabul qilish."""
    if message.text == "⏩ O'tkazib yuborish":
        await state.update_data(translator="AniBro")
    else:
        await state.update_data(translator=message.text.strip())
    await state.set_state(AddAnimeStates.poster)
    await message.answer(
        "◈ Poster rasmini yuboring (yoki o'tkazib yuboring):",
        reply_markup=skip_keyboard(),
    )


@router.message(AddAnimeStates.poster, is_admin, F.photo)
async def add_anime_poster_photo(message: Message, state: FSMContext) -> None:
    """Poster rasm (photo) qabul qilish."""
    file_id = message.photo[-1].file_id
    await state.update_data(poster_file_id=file_id, poster_url="")
    await state.set_state(AddAnimeStates.is_vip)
    await message.answer(
        "✅ <b>Poster rasm sifatida qabul qilindi.</b>\n\n"
        "💎 Bu anime VIP bo'ladimi?",
        reply_markup=vip_choice_keyboard(),
    )


@router.message(AddAnimeStates.poster, is_admin, F.text.startswith("http"))
async def add_anime_poster_url(message: Message, state: FSMContext) -> None:
    """Poster rasm (URL) qabul qilish."""
    url = message.text.strip()
    await state.update_data(poster_file_id="", poster_url=url)
    await state.set_state(AddAnimeStates.is_vip)
    await message.answer(
        f"✅ <b>Poster URL sifatida qabul qilindi:</b>\n<code>{url}</code>\n\n"
        "💎 Bu anime VIP bo'ladimi?",
        reply_markup=vip_choice_keyboard(),
    )


@router.message(AddAnimeStates.poster, is_admin)
async def add_anime_poster_other(message: Message, state: FSMContext) -> None:
    """Posterni o'tkazib yuborish yoki noto'g'ri kiritish."""
    if message.text == "⏩ O'tkazib yuborish":
        await state.update_data(poster_file_id="", poster_url="")
        await state.set_state(AddAnimeStates.is_vip)
        await message.answer(
            "⏩ <b>Poster o'tkazib yuborildi.</b>\n\n"
            "💎 Bu anime VIP bo'ladimi?",
            reply_markup=vip_choice_keyboard(),
        )
    else:
        await message.answer(
            "🖼 <b>Iltimos, rasm yuboring yoki rasm (URL) manzilini kiriting.</b>\n\n"
            "⏩ O'tkazib yuborish uchun tugmani bosing."
        )


@router.message(AddAnimeStates.is_vip, is_admin)
async def add_anime_is_vip(message: Message, state: FSMContext) -> None:
    """VIP holatini belgilash va animeni saqlash."""
    if message.text == "Ha (VIP)":
        is_vip = 1
    elif message.text == "Yo'q (Oddiy)":
        is_vip = 0
    else:
        await message.answer("\u25B8 Iltimos, tugmalardan tanlang.")
        return

    data = await state.get_data()

    try:
        anime_id = await AnimeModel.create(
            title=data["title"],
            code=data["code"],
            description=data.get("description", ""),
            genre=data.get("genre", ""),
            season_count=data.get("season_count", 1),
            total_episodes=data.get("total_episodes", 0),
            poster_file_id=data.get("poster_file_id", ""),
            poster_url=data.get("poster_url", ""),
            status=data.get("status", "Tugallangan"),
            translator=data.get("translator", "AniBro"),
            is_vip=is_vip,
        )
        await state.clear()
        
        vip_text = "◆ VIP" if is_vip else "○ Oddiy"
        await message.answer(
            f"✔ <b>Anime muvaffaqiyatli qo'shildi!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"◈ Nom: {data['title']}\n"
            f"◈ Kod: {data['code']}\n"
            f"◈ Janr: {data.get('genre', '---')}\n"
            f"◈ Sezonlar: {data.get('season_count', 1)}\n"
            f"◈ Holat: {vip_text}\n"
            f"◈ ID: {anime_id}",
            reply_markup=admin_main_menu(),
        )
    except Exception as e:
        logger.error(f"Anime qo'shishda xatolik: {e}")
        await message.answer(
            f"✖ <b>Xatolik yuz berdi!</b>\n"
            f"Ma'lumotlar bazasiga saqlashda muammo bo'ldi.\n\n"
            f"Xato xabari: <code>{str(e)}</code>",
            reply_markup=admin_main_menu()
        )


# ==============================================================
# ANIME TAHRIRLASH
# ==============================================================

@router.message(F.text == "📝 Anime tahrirlash", is_admin)
async def edit_anime_start(message: Message, state: FSMContext) -> None:
    """Anime tahrirlash - anime tanlash."""
    anime_list = await AnimeModel.get_all(limit=50)
    if not anime_list:
        await message.answer("\u25B8 Hozircha animelar mavjud emas.")
        return
    await state.set_state(EditAnimeStates.select_anime)
    await message.answer(
        "<b>\u270E Anime tahrirlash</b>\n\nTahrirlash uchun animeni tanlang:",
        reply_markup=anime_select_keyboard(anime_list, "edit_anime_select"),
    )


@router.callback_query(F.data.startswith("edit_anime_select:"))
async def edit_anime_selected(callback: CallbackQuery, state: FSMContext) -> None:
    """Tahrirlash uchun anime tanlangan."""
    anime_id = int(callback.data.split(":")[1])
    anime = await AnimeModel.get_by_id(anime_id)
    if not anime:
        await callback.answer("Anime topilmadi.")
        return

    await state.update_data(edit_anime_id=anime_id)
    await state.set_state(EditAnimeStates.select_field)

    await callback.message.edit_text(
        f"<b>\u270E {anime['title']} tahrirlash</b>\n\n"
        "Qaysi maydonni tahrirlaysiz?\n\n"
        "1. title - Nom\n"
        "2. description - Tavsif\n"
        "3. genre - Janr\n"
        "4. season_count - Sezonlar soni\n"
        "5. total_episodes - Qismlar soni\n"
        "6. status - Holati\n"
        "7. translator - Tarjimon\n"
        "8. is_vip - VIP holati (0 yoki 1)\n"
        "9. poster_url - Rasm URL\n"
        "10. poster_file_id - Rasm ID\n\n"
        "Maydon nomini yozing (masalan: <code>status</code>):"
    )
    await callback.answer()


@router.message(EditAnimeStates.select_field, is_admin)
async def edit_anime_field_selected(message: Message, state: FSMContext) -> None:
    """Tahrirlash uchun maydon tanlangan."""
    field = message.text.strip().lower()
    allowed_fields = [
        "title", "description", "genre", "season_count", 
        "total_episodes", "status", "translator", "is_vip", "poster_url", "poster_file_id"
    ]

    if field not in allowed_fields:
        await message.answer(
            f"\u2716 Noto'g'ri maydon. Ruxsat berilgan maydonlar:\n"
            f"{', '.join(allowed_fields)}"
        )
        return

    await state.update_data(edit_field=field)
    await state.set_state(EditAnimeStates.new_value)
    await message.answer(f"\u25B8 <b>{field}</b> uchun yangi qiymat kiriting:")


@router.message(EditAnimeStates.new_value, is_admin)
async def edit_anime_new_value(message: Message, state: FSMContext) -> None:
    """Yangi qiymatni saqlash."""
    data = await state.get_data()
    anime_id = data["edit_anime_id"]
    field = data["edit_field"]
    value = message.text.strip()

    # Raqamli maydonlar uchun tekshirish
    if field in ("season_count", "total_episodes", "is_vip"):
        try:
            value = int(value)
        except ValueError:
            await message.answer("\u2716 Iltimos, raqam kiriting:")
            return

    await state.clear()
    try:
        await AnimeModel.update(anime_id, **{field: value})
        await message.answer(
            f"✔ <b>Anime yangilandi!</b>\n\n"
            f"▸ Maydon: {field}\n"
            f"▸ Yangi qiymat: {value}",
            reply_markup=admin_main_menu(),
        )
    except Exception as e:
        logger.error(f"Anime update error: {e}")
        await message.answer(
            f"✖ <b>Yangilashda xatolik!</b>\n"
            f"Xato: <code>{str(e)}</code>",
            reply_markup=admin_main_menu()
        )



# ==============================================================
# ANIME O'CHIRISH
# ==============================================================

@router.message(F.text == "❌ Anime o'chirish", is_admin)
async def delete_anime_start(message: Message) -> None:
    """Anime o'chirish - anime tanlash."""
    anime_list = await AnimeModel.get_all(limit=50)
    if not anime_list:
        await message.answer("\u25B8 Hozircha animelar mavjud emas.")
        return
    await message.answer(
        "<b>\u2716 Anime o'chirish</b>\n\nO'chirish uchun animeni tanlang:",
        reply_markup=anime_select_keyboard(anime_list, "delete_anime_confirm"),
    )


@router.callback_query(F.data.startswith("delete_anime_confirm:"))
async def delete_anime_confirmed(callback: CallbackQuery) -> None:
    """Animeni o'chirish tasdiqlash."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Sizda ruxsat yo'q.")
        return

    anime_id = int(callback.data.split(":")[1])
    anime = await AnimeModel.get_by_id(anime_id)

    if not anime:
        await callback.answer("Anime topilmadi.")
        return

    try:
        await AnimeModel.delete(anime_id)
        await callback.message.edit_text(
            f"✅ <b>\"{anime['title']}\"</b> muvaffaqiyatli o'chirildi!"
        )
    except Exception as e:
        logger.error(f"Anime delete error: {e}")
        await callback.message.answer(f"✖ <b>O'chirishda xatolik:</b> {e}")

    await callback.answer()


@router.callback_query(F.data.startswith("fix_anime_poster:"), is_admin)
async def fix_anime_poster_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Quick fix for broken anime poster."""
    anime_id = int(callback.data.split(":")[1])
    await state.update_data(edit_anime_id=anime_id, edit_field="poster_file_id")
    await state.set_state(EditAnimeStates.new_value)
    
    await callback.message.answer(
        "🖼 <b>Posterni yangilash (Quick Fix)</b>\n\nYangi poster rasm yuboring yoki rasm URL manzilini kiriting:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()
