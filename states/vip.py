"""
states/vip.py - VIP to'lov uchun FSM holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class VipPaymentStates(StatesGroup):
    """VIP to'lov jarayoni holatlari."""
    waiting_screenshot = State()  # Screenshot kutish


class VipPlanStates(StatesGroup):
    """VIP plan yaratish holatlari (admin)."""
    name = State()             # Plan nomi
    price = State()            # Narxi
    duration_days = State()    # Davomiyligi (kun)
    card_number = State()      # Karta raqami
