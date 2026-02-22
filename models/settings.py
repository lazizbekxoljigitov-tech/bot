"""
models/settings.py - Bot sozlamalari modeli (key-value).
"""

from database import Database


class SettingsModel:
    """Bot sozlamalari bilan ishlash."""

    @staticmethod
    async def get(key: str, default: str = "") -> str:
        """Sozlamani olish."""
        db = await Database.connect()
        cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row["value"] if row else default

    @staticmethod
    async def set(key: str, value: str) -> None:
        """Sozlamani o'rnatish."""
        db = await Database.connect()
        await db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        await db.commit()

    @staticmethod
    async def get_all() -> dict:
        """Barcha sozlamalarni olish."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM settings")
        rows = await cursor.fetchall()
        return {r["key"]: r["value"] for r in rows}
