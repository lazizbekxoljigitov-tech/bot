"""
models/admin.py - Adminlarni boshqarish modeli.
"""

from database import Database
from config import ADMIN_IDS


class AdminModel:
    """Adminlar jadvali bilan ishlash."""

    @staticmethod
    async def is_admin(telegram_id: int) -> bool:
        """Foydalanuvchi admin ekanligini tekshirish."""
        # Avval config dagi asosiy adminlarni tekshiramiz
        if telegram_id in ADMIN_IDS:
            return True
        
        # Keyin bazadagi qo'shilgan adminlarni tekshiramiz
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        return row is not None

    @staticmethod
    async def add_admin(telegram_id: int, full_name: str = "", role: str = "admin") -> bool:
        """Yangi admin qo'shish."""
        db = await Database.connect()
        try:
            await db.execute(
                "INSERT INTO admins (telegram_id, full_name, role) VALUES (?, ?, ?)",
                (telegram_id, full_name, role),
            )
            await db.commit()
            return True
        except Exception:
            return False

    @staticmethod
    async def remove_admin(telegram_id: int) -> bool:
        """Adminni o'chirish."""
        db = await Database.connect()
        await db.execute("DELETE FROM admins WHERE telegram_id = ?", (telegram_id,))
        await db.commit()
        return True

    @staticmethod
    async def get_all() -> list[dict]:
        """Barcha adminlarni olish."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM admins ORDER BY added_at DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
