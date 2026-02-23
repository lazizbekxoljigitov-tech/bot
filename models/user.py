"""
models/user.py - User model with async CRUD operations.
Handles user registration, VIP status, and profile queries.
"""

from database import Database


class UserModel:
    """Provides async database operations for the users table."""

    @staticmethod
    async def create_or_update(telegram_id: int, full_name: str, username: str) -> dict | None:
        """Register a new user or update existing user info. Returns the user row."""
        db = await Database.connect()
        await db.execute(
            """
            INSERT INTO users (telegram_id, full_name, username)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                full_name = excluded.full_name,
                username = excluded.username
            """,
            (telegram_id, full_name, username),
        )
        await db.commit()
        return await UserModel.get_by_telegram_id(telegram_id)

    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> dict | None:
        """Fetch a user row by their Telegram ID."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    async def get_by_id(user_id: int) -> dict | None:
        """Fetch a user row by internal database ID."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    async def set_vip(telegram_id: int, expire_date: str) -> None:
        """Activate VIP status for a user with an expiration date."""
        db = await Database.connect()
        await db.execute(
            "UPDATE users SET is_vip = 1, vip_expire_date = ? WHERE telegram_id = ?",
            (expire_date, telegram_id),
        )
        await db.commit()

    @staticmethod
    async def remove_vip(telegram_id: int) -> None:
        """Deactivate VIP status for a user."""
        db = await Database.connect()
        await db.execute(
            "UPDATE users SET is_vip = 0, vip_expire_date = NULL WHERE telegram_id = ?",
            (telegram_id,),
        )
        await db.commit()

    @staticmethod
    async def get_all_users() -> list[dict]:
        """Retrieve all registered users."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM users ORDER BY joined_date DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def get_count() -> int:
        """Return the total number of registered users."""
        db = await Database.connect()
        cursor = await db.execute("SELECT COUNT(*) as cnt FROM users")
        row = await cursor.fetchone()
        return row["cnt"] if row else 0


    @staticmethod
    async def get_vip_users() -> list[dict]:
        """Retrieve all VIP users."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM users WHERE is_vip = 1 ORDER BY vip_expire_date DESC"
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
