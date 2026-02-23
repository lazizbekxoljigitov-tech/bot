"""
states/shorts.py - Shorts qo'shish uchun FSM holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class AddShortsStates(StatesGroup):
    """Shorts qo'shish jarayoni holatlari."""
    select_anime = State()  # Anime tanlash
    video = State()         # Qisqa video fayl

class EditShortsStates(StatesGroup):
    """Shorts tahrirlash jarayoni holatlari."""
    waiting_video = State() # Yangi video fayl

