"""
states/comment.py - Izoh qoldirish uchun FSM holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class CommentStates(StatesGroup):
    """Izoh yozish jarayoni holatlari."""
    waiting_text = State()  # Izoh matnini kutish
