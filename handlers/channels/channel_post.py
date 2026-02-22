"""
handlers/channels/channel_post.py - Kanalga post yuborish handleri.
Admin to'g'ridan-to'g'ri kanal ID kiritadi va shu kanalga post ketadi.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from states.channel import ChannelPostStates
from models.anime import AnimeModel
from models.episode import EpisodeModel
from models.admin import AdminModel
from keyboards.reply import channel_post_menu, admin_main_menu, cancel_keyboard
from keyboards.inline import (
    anime_select_keyboard,
    channel_big_post_keyboard,
    channel_post_keyboard,
)
from services.anime_service import AnimeService
from loader import bot

logger = logging.getLogger(__name__)
router = Router(name="admin_channel_post")

async def is_admin(message: Message) -> bool:
    return await AdminModel.is_admin(message.from_user.id)

@router.message(F.text == "📢 Kanalga post", is_admin)
async def channel_post_start(message: Message, state: FSMContext) -> None:
    """Kanalga post - anime tanlash."""
    anime_list = await AnimeModel.get_all(limit=50)
    if not anime_list:
        await message.answer("\u25B8 Avval anime qo'shing.")
        return
    await state.set_state(ChannelPostStates.select_anime)
    await message.answer(
        "<b>\u27A4 Kanalga post</b>\n\nPost uchun animeni tanlang:",
        reply_markup=anime_select_keyboard(anime_list, "ch_post_anime"),
    )

@router.callback_query(F.data.startswith("ch_post_anime:"))
async def channel_post_anime_selected(callback: CallbackQuery, state: FSMContext) -> None:
    """Anime tanlangan - kanal ID/username kiritishni so'rash."""
    anime_id = int(callback.data.split(":")[1])
    await state.update_data(post_anime_id=anime_id)
    await state.set_state(ChannelPostStates.enter_channel)
    await callback.message.edit_text(
        "\u25B8 Kanalning ID yoki username kiriting\n\n"
        "Masalan:\n"
        "  <code>-100123456789</code>\n"
        "  <code>@kanal_nomi</code>\n\n"
        "Bot o'sha kanalda admin bo'lishi shart!"
    )
    await callback.answer()

@router.message(ChannelPostStates.enter_channel, is_admin)
async def channel_entered(message: Message, state: FSMContext) -> None:
    """Kanal kiritildi - format tanlashga o'tish."""
    channel_input = message.text.strip()
    await state.update_data(target_channel=channel_input)
    await state.set_state(ChannelPostStates.select_format)
    await message.answer(
        f"\u25B8 Kanal: <code>{channel_input}</code>\n\n"
        "Post formatini tanlang:",
        reply_markup=channel_post_menu(),
    )

@router.message(ChannelPostStates.select_format, is_admin)
async def send_channel_post(message: Message, state: FSMContext) -> None:
    """Tanlangan formatda kiritilgan kanalga post yuborish."""
    data = await state.get_data()
    anime_id = data.get("post_anime_id")
    channel = data.get("target_channel")
    await state.clear()

    anime = await AnimeModel.get_by_id(anime_id)
    if not anime:
        await message.answer("\u2716 Anime topilmadi.", reply_markup=admin_main_menu())
        return

    bot_info = await bot.get_me()
    bot_username = bot_info.username

    try:
        if message.text == "🖼 Katta post":
            # Katta post: poster + to'liq info + tugmalar
            text = await AnimeService.get_anime_info_text(anime_id)
            poster = AnimeService.get_poster(anime)
            
            if poster:
                await bot.send_photo(
                    chat_id=channel,
                    photo=poster,
                    caption=text,
                    reply_markup=channel_big_post_keyboard(anime_id, bot_username),
                )
            else:
                await bot.send_message(
                    chat_id=channel,
                    text=text,
                    reply_markup=channel_big_post_keyboard(anime_id, bot_username),
                )
            await message.answer(
                f"\u2714 Katta post <code>{channel}</code> kanalga yuborildi!",
                reply_markup=admin_main_menu(),
            )

        elif message.text == "📄 Kichik post":
            # Kichik post: nom + qism soni + tugma
            ep_count = await EpisodeModel.get_episode_count(anime_id)
            text = (
                f"<b>{anime['title']}</b>\n"
                f"\u25B8 Qismlar: {ep_count}\n"
                f"\u25B8 Janr: {anime['genre']}"
            )
            await bot.send_message(
                chat_id=channel,
                text=text,
                reply_markup=channel_post_keyboard(anime_id, bot_username),
            )
            await message.answer(
                f"\u2714 Kichik post <code>{channel}</code> kanalga yuborildi!",
                reply_markup=admin_main_menu(),
            )
        else:
            await message.answer(
                "\u25B8 Iltimos, format tugmasini bosing.",
                reply_markup=channel_post_menu(),
            )
            return

    except Exception as e:
        logger.error("Kanalga post xatolik: %s", str(e))
        await message.answer(
            f"\u2716 Xatolik! Kanalga post yuborib bo'lmadi.\n\n"
            f"Sabab: <code>{str(e)[:200]}</code>\n\n"
            "Bot o'sha kanalda admin ekanligini tekshiring.",
            reply_markup=admin_main_menu(),
        )
