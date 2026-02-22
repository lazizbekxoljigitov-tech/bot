"""
states/anime.py - Anime qo'shish/tahrirlash uchun FSM holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class AddAnimeStates(StatesGroup):
    """Yangi anime qo'shish jarayoni holatlari."""
    title = State()          # Anime nomi
    code = State()           # Anime kodi (unique)
    description = State()    # Anime tavsifi
    genre = State()          # Janri
    season_count = State()   # Sezonlar soni
    total_episodes = State() # Umumiy qismlar soni
    poster = State()         # Poster rasm (file_id)
    is_vip = State()         # VIP yoki oddiy


class EditAnimeStates(StatesGroup):
    """Anime tahrirlash holatlari."""
    select_anime = State()   # Tahrirlash uchun anime tanlash
    select_field = State()   # Qaysi maydonni tahrirlash
    new_value = State()      # Yangi qiymat kiritish
