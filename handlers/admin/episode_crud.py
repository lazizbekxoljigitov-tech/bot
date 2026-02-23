"""
handlers/admin/episode_crud.py - Qism CRUD handlerlari (admin).
Qism qo'shish, tahrirlash va o'chirish.
"""

import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from states.episode import AddEpisodeStates, EditEpisodeStates
from models.anime import AnimeModel
from models.episode import EpisodeModel
from models.admin import AdminModel
from keyboards.reply import cancel_keyboard, vip_choice_keyboard, admin_main_menu
from keyboards.inline import anime_select_keyboard

logger = logging.getLogger(__name__)
router = Router(name="admin_episode_crud")


async def is_admin(message: Message) -> bool:
    return await AdminModel.is_admin(message.from_user.id)


# ==============================================================
# QISM QO'SHISH
# ==============================================================

@router.message(F.text == "➕ Qism qo'shish", is_admin)
async def add_episode_start(message: Message, state: FSMContext) -> None:
    """Qism qo'shish - anime tanlash."""
    anime_list = await AnimeModel.get_all(limit=50)
    if not anime_list:
        await message.answer("\u25B8 Avval anime qo'shing.")
        return
    await state.set_state(AddEpisodeStates.select_anime)
    await message.answer(
        "<b>\u002B Qism qo'shish</b>\n\nQaysi animega qism qo'shmoqchisiz?",
        reply_markup=anime_select_keyboard(anime_list, "add_ep_anime"),
    )


@router.callback_query(F.data.startswith("add_ep_anime:"))
async def add_episode_anime_selected(callback: CallbackQuery, state: FSMContext) -> None:
    """Qism qo'shish uchun anime tanlangan."""
    anime_id = int(callback.data.split(":")[1])
    await state.update_data(anime_id=anime_id)
    await state.set_state(AddEpisodeStates.season_number)

    anime = await AnimeModel.get_by_id(anime_id)
    await callback.message.edit_text(
        f"<b>{anime['title']}</b>\n\n"
        "\u25B8 Sezon raqamini kiriting:"
    )
    await callback.answer()


@router.message(AddEpisodeStates.season_number, is_admin)
async def add_episode_season(message: Message, state: FSMContext) -> None:
    """Sezon raqamini qabul qilish."""
    try:
        season = int(message.text.strip())
        if season < 1:
            raise ValueError
    except ValueError:
        await message.answer("\u2716 To'g'ri raqam kiriting:")
        return
    await state.update_data(season_number=season)
    await state.set_state(AddEpisodeStates.episode_number)
    await message.answer("\u25B8 Qism raqamini kiriting:")


@router.message(AddEpisodeStates.episode_number, is_admin)
async def add_episode_number(message: Message, state: FSMContext) -> None:
    """Qism raqamini qabul qilish."""
    try:
        ep_num = int(message.text.strip())
        if ep_num < 1:
            raise ValueError
    except ValueError:
        await message.answer("\u2716 To'g'ri raqam kiriting:")
        return
    await state.update_data(episode_number=ep_num)
    await state.set_state(AddEpisodeStates.title)
    await message.answer(
        "\u25B8 Qism nomini kiriting (ixtiyoriy, bo'sh qoldirsa ham bo'ladi):",
        reply_markup=cancel_keyboard(),
    )


@router.message(AddEpisodeStates.title, is_admin)
async def add_episode_title(message: Message, state: FSMContext) -> None:
    """Qism nomini qabul qilish."""
    await state.update_data(title=message.text.strip())
    await state.set_state(AddEpisodeStates.video)
    await message.answer(
        "\u25B8 Qism videosini yuboring:",
        reply_markup=cancel_keyboard(),
    )


@router.message(AddEpisodeStates.video, is_admin, F.video)
async def add_episode_video(message: Message, state: FSMContext) -> None:
    """Video faylni qabul qilish."""
    file_id = message.video.file_id
    await state.update_data(video_file_id=file_id)
    await state.set_state(AddEpisodeStates.is_vip)
    await message.answer(
        "\u25B8 Bu qism VIP bo'ladimi?",
        reply_markup=vip_choice_keyboard(),
    )


@router.message(AddEpisodeStates.video, is_admin)
async def add_episode_video_invalid(message: Message, state: FSMContext) -> None:
    """Video bo'lmagan xabar."""
    await message.answer("\u25B8 Iltimos, video fayl yuboring.")


@router.message(AddEpisodeStates.is_vip, is_admin)
async def add_episode_is_vip(message: Message, state: FSMContext) -> None:
    """VIP holatini belgilash va qismni saqlash."""
    if message.text == "Ha (VIP)":
        is_vip = 1
    elif message.text == "Yo'q (Oddiy)":
        is_vip = 0
    else:
        await message.answer("\u25B8 Tugmalardan tanlang.")
        return

    data = await state.get_data()

    try:
        episode_id = await EpisodeModel.create(
            anime_id=data["anime_id"],
            season_number=data["season_number"],
            episode_number=data["episode_number"],
            title=data.get("title", ""),
            video_file_id=data["video_file_id"],
            is_vip=is_vip,
        )
        await state.clear()

        anime = await AnimeModel.get_by_id(data["anime_id"])
        vip_text = "◆ VIP" if is_vip else "○ Oddiy"

        await message.answer(
            f"✔ <b>Qism muvaffaqiyatli qo'shildi!</b>\n\n"
            f"▸ Anime: {anime['title'] if anime else '---'}\n"
            f"▸ Sezon: {data['season_number']}\n"
            f"▸ Qism: {data['episode_number']}\n"
            f"▸ Holat: {vip_text}\n"
            f"▸ ID: {episode_id}",
            reply_markup=admin_main_menu(),
        )
    except Exception as e:
        logger.error(f"Qism qo'shishda xatolik: {e}")
        await message.answer(
            f"✖ <b>Xatolik yuz berdi!</b>\n"
            f"Qismni ma'lumotlar bazasiga saqlashda muammo yuzaga keldi.\n\n"
            f"Xato: <code>{str(e)}</code>",
            reply_markup=admin_main_menu()
        )


# ==============================================================
# QISM TAHRIRLASH
# ==============================================================

@router.message(F.text == "📝 Qism tahrirlash", is_admin)
async def edit_episode_start(message: Message, state: FSMContext) -> None:
    """Qism tahrirlash - anime tanlash."""
    anime_list = await AnimeModel.get_all(limit=50)
    if not anime_list:
        await message.answer("\u25B8 Hozircha animelar mavjud emas.")
        return
    await state.set_state(EditEpisodeStates.select_anime)
    await message.answer(
        "<b>\u270E Qism tahrirlash</b>\n\nAvval animeni tanlang:",
        reply_markup=anime_select_keyboard(anime_list, "edit_ep_anime"),
    )


@router.callback_query(F.data.startswith("edit_ep_anime:"))
async def edit_episode_anime_selected(callback: CallbackQuery, state: FSMContext) -> None:
    """Tahrirlanadigan qism uchun anime tanlangan."""
    anime_id = int(callback.data.split(":")[1])
    episodes = await EpisodeModel.get_all_for_anime(anime_id)

    if not episodes:
        await callback.message.edit_text("\u25B8 Bu animeda qismlar yo'q.")
        await callback.answer()
        return

    await state.update_data(edit_anime_id=anime_id)
    await state.set_state(EditEpisodeStates.select_episode)

    text = "<b>Qismni tanlang:</b>\n\n"
    for ep in episodes:
        text += f"\u25B8 S{ep['season_number']}E{ep['episode_number']} - {ep['title']} (ID: {ep['id']})\n"
    text += "\nQism ID raqamini kiriting:"

    await callback.message.edit_text(text)
    await callback.answer()


@router.message(EditEpisodeStates.select_episode, is_admin)
async def edit_episode_selected(message: Message, state: FSMContext) -> None:
    """Tahrirlash uchun qism tanlangan."""
    try:
        episode_id = int(message.text.strip())
    except ValueError:
        await message.answer("\u2716 To'g'ri ID kiriting:")
        return

    episode = await EpisodeModel.get_by_id(episode_id)
    if not episode:
        await message.answer("\u2716 Qism topilmadi. Qayta kiriting:")
        return

    await state.update_data(edit_episode_id=episode_id)
    await state.set_state(EditEpisodeStates.select_field)
    await message.answer(
        f"<b>S{episode['season_number']}E{episode['episode_number']}</b>\n\n"
        "Qaysi maydonni o'zgartirasiz?\n\n"
        "1. title - Nomi\n"
        "2. season_number - Sezon raqami\n"
        "3. episode_number - Qism raqami\n"
        "4. is_vip - VIP holati (0 yoki 1)\n\n"
        "Maydon nomini yozing:"
    )


@router.message(EditEpisodeStates.select_field, is_admin)
async def edit_episode_field(message: Message, state: FSMContext) -> None:
    """Tahrirlash maydoni tanlangan."""
    field = message.text.strip().lower()
    allowed = ["title", "season_number", "episode_number", "is_vip"]
    if field not in allowed:
        await message.answer(f"\u2716 Ruxsat berilgan maydonlar: {', '.join(allowed)}")
        return

    await state.update_data(edit_field=field)
    await state.set_state(EditEpisodeStates.new_value)
    await message.answer(f"\u25B8 <b>{field}</b> uchun yangi qiymat kiriting:")


@router.message(EditEpisodeStates.new_value, is_admin)
async def edit_episode_save(message: Message, state: FSMContext) -> None:
    """Yangi qiymatni saqlash."""
    data = await state.get_data()
    field = data["edit_field"]
    value = message.text.strip()

    if field in ("season_number", "episode_number", "is_vip"):
        try:
            value = int(value)
        except ValueError:
            await message.answer("\u2716 Raqam kiriting:")
            return

    await state.clear()
    try:
        await EpisodeModel.update(data["edit_episode_id"], **{field: value})
        await message.answer(
            f"✔ <b>Qism yangilandi!</b>\n\n"
            f"▸ Maydon: {field}\n"
            f"▸ Yangi qiymat: {value}",
            reply_markup=admin_main_menu(),
        )
    except Exception as e:
        logger.error(f"Episode update error: {e}")
        await message.answer(
            f"✖ <b>Yangilashda xatolik!</b>\n"
            f"Xato: <code>{str(e)}</code>",
            reply_markup=admin_main_menu()
        )



# ==============================================================
# QISM O'CHIRISH
# ==============================================================

@router.message(F.text == "❌ Qism o'chirish", is_admin)
async def delete_episode_start(message: Message) -> None:
    """Qism o'chirish - anime tanlash."""
    anime_list = await AnimeModel.get_all(limit=50)
    if not anime_list:
        await message.answer("\u25B8 Hozircha animelar mavjud emas.")
        return
    await message.answer(
        "<b>\u2716 Qism o'chirish</b>\n\nAvval animeni tanlang:",
        reply_markup=anime_select_keyboard(anime_list, "del_ep_anime"),
    )


@router.callback_query(F.data.startswith("del_ep_anime:"))
async def delete_episode_anime_selected(callback: CallbackQuery) -> None:
    """O'chirish uchun anime tanlangan - qismlar ro'yxati."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Ruxsat yo'q.")
        return

    anime_id = int(callback.data.split(":")[1])
    episodes = await EpisodeModel.get_all_for_anime(anime_id)

    if not episodes:
        await callback.message.edit_text("\u25B8 Bu animeda qismlar yo'q.")
        await callback.answer()
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for ep in episodes:
        builder.button(
            text=f"\u2716 S{ep['season_number']}E{ep['episode_number']}",
            callback_data=f"del_ep_confirm:{ep['id']}",
        )
    builder.adjust(3)

    await callback.message.edit_text(
        "<b>O'chirish uchun qismni tanlang:</b>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("del_ep_confirm:"))
async def delete_episode_confirmed(callback: CallbackQuery) -> None:
    """Qismni o'chirish."""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Ruxsat yo'q.")
        return

    episode_id = int(callback.data.split(":")[1])
    episode = await EpisodeModel.get_by_id(episode_id)

    if not episode:
        await callback.answer("Qism topilmadi.")
        return

    try:
        await EpisodeModel.delete(episode_id)
        await callback.message.edit_text(
            f"✅ S{episode['season_number']}E{episode['episode_number']} o'chirildi!"
        )
    except Exception as e:
        logger.error(f"Episode delete error: {e}")
        await callback.message.answer(f"✖ <b>O'chirishda xatolik:</b> {e}")

    await callback.answer()


@router.callback_query(F.data.startswith("fix_ep_video:"), is_admin)
async def fix_episode_video_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Quick fix for broken episode video."""
    episode_id = int(callback.data.split(":")[1])
    # Hozircha episode_crud da faqat text orqali yangilash bor
    # EditEpisodeStates ga video kiritish holatini qo'shishimiz kerak yoki new_value ga video ham qabul qiladigan qilishimiz kerak
    # Biz EditEpisodeStates ga video holatini qo'shamiz
    from states.episode import EditEpisodeStates
    await state.update_data(edit_episode_id=episode_id, edit_field="video_file_id")
    await state.set_state(EditEpisodeStates.new_value)
    
    await callback.message.answer(
        "🎞 <b>Videoni yangilash (Quick Fix)</b>\n\nYangi video faylni yuboring:",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()

