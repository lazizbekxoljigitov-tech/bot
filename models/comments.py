"""
models/comments.py - Comments model with async CRUD operations.
Handles user comments on anime.
"""

from database import Database


class CommentsModel:
    """Provides async database operations for the comments table."""

    @staticmethod
    async def add(user_id: int, anime_id: int, comment_text: str) -> int:
        """Add a new comment and return its ID."""
        db = await Database.connect()
        cursor = await db.execute(
            "INSERT INTO comments (user_id, anime_id, comment_text) VALUES (?, ?, ?)",
            (user_id, anime_id, comment_text),
        )
        await db.commit()
        return cursor.lastrowid

    @staticmethod
    async def get_by_anime(anime_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
        """Get comments for an anime with user info, paginated."""
        db = await Database.connect()
        cursor = await db.execute(
            """
            SELECT c.*, u.full_name, u.username, u.is_vip
            FROM comments c
            INNER JOIN users u ON c.user_id = u.id
            WHERE c.anime_id = ?
            ORDER BY c.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (anime_id, limit, offset),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def get_comment_count(anime_id: int) -> int:
        """Return the total number of comments for an anime."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM comments WHERE anime_id = ?", (anime_id,)
        )
        row = await cursor.fetchone()
        return row["cnt"] if row else 0

    @staticmethod
    async def delete(comment_id: int) -> None:
        """Delete a comment by its ID."""
        db = await Database.connect()
        await db.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        await db.commit()
