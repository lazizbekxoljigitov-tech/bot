"""
states/search.py - Qidiruv uchun FSM holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    """Qidiruv jarayoni holatlari."""
    waiting_query = State()   # Qidiruv so'zini kutish
    waiting_genre = State()   # Janr nomini kutish
    waiting_code = State()    # Anime kodini kutish
