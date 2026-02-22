"""
states/episode.py - Qism qo'shish/tahrirlash uchun FSM holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class AddEpisodeStates(StatesGroup):
    """Yangi qism qo'shish jarayoni holatlari."""
    select_anime = State()    # Qaysi animega qism qo'shish
    season_number = State()   # Sezon raqami
    episode_number = State()  # Qism raqami
    title = State()           # Qism nomi
    video = State()           # Video fayl (file_id)
    is_vip = State()          # VIP yoki oddiy


class EditEpisodeStates(StatesGroup):
    """Qism tahrirlash holatlari."""
    select_anime = State()    # Anime tanlash
    select_episode = State()  # Qism tanlash
    select_field = State()    # Maydon tanlash
    new_value = State()       # Yangi qiymat kiritish
