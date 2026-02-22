"""
states/channel.py - Kanal boshqarish uchun FSM holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class ChannelPostStates(StatesGroup):
    """Kanalga post jo'natish holatlari."""
    select_anime = State()     # Anime tanlash
    enter_channel = State()    # Kanal ID/link kiritish
    select_format = State()    # Post formati tanlash


class AddChannelStates(StatesGroup):
    """Yangi kanal qo'shish holatlari (majburiy obuna)."""
    channel_id = State()
    channel_link = State()
