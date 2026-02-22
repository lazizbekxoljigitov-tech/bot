"""
models/favorites.py - Favorites model with async CRUD operations.
Handles user favorite anime bookmarking.
"""

from database import Database


class FavoritesModel:
    """Provides async database operations for the favorites table."""

    @staticmethod
    async def add(user_id: int, anime_id: int) -> bool:
        """Add an anime to user's favorites. Returns True if added, False if already exists."""
        db = await Database.connect()
        try:
            await db.execute(
                "INSERT INTO favorites (user_id, anime_id) VALUES (?, ?)",
                (user_id, anime_id),
            )
            await db.commit()
            return True
        except Exception:
            return False

    @staticmethod
    async def remove(user_id: int, anime_id: int) -> None:
        """Remove an anime from user's favorites."""
        db = await Database.connect()
        await db.execute(
            "DELETE FROM favorites WHERE user_id = ? AND anime_id = ?",
            (user_id, anime_id),
        )
        await db.commit()

    @staticmethod
    async def get_by_user(user_id: int) -> list[dict]:
        """Get all favorite anime for a user with anime details."""
        db = await Database.connect()
        cursor = await db.execute(
            """
            SELECT a.* FROM anime a
            INNER JOIN favorites f ON a.id = f.anime_id
            WHERE f.user_id = ?
            ORDER BY f.id DESC
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def is_favorite(user_id: int, anime_id: int) -> bool:
        """Check if an anime is in the user's favorites."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT id FROM favorites WHERE user_id = ? AND anime_id = ?",
            (user_id, anime_id),
        )
        row = await cursor.fetchone()
        return row is not None
