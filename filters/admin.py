"""
filters/admin.py - Centralized admin filters.
"""

from aiogram import types
from aiogram.filters import Filter
from models.admin import AdminModel

class IsAdminFilter(Filter):
    """Checks if a user is an admin (either in config or database)."""
    async def __call__(self, event: types.Message | types.CallbackQuery) -> bool:
        return await AdminModel.is_admin(event.from_user.id)

# Shorthand for simple usage
is_admin = IsAdminFilter()
