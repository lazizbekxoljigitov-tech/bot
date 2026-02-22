"""
models/shorts.py - Shorts model with async CRUD operations.
Handles short anime clips management and view counting.
"""

from database import Database


class ShortsModel:
    """Provides async database operations for the shorts table."""

    @staticmethod
    async def create(anime_id: int, short_video_file_id: str) -> int:
        """Create a new short clip entry and return its ID."""
        db = await Database.connect()
        cursor = await db.execute(
            "INSERT INTO shorts (anime_id, short_video_file_id) VALUES (?, ?)",
            (anime_id, short_video_file_id),
        )
        await db.commit()
        return cursor.lastrowid

    @staticmethod
    async def get_by_id(short_id: int) -> dict | None:
        """Fetch a short clip by its ID."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM shorts WHERE id = ?", (short_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    async def get_all(limit: int = 50, offset: int = 0) -> list[dict]:
        """Get all shorts with anime info, paginated."""
        db = await Database.connect()
        cursor = await db.execute(
            """
            SELECT s.*, a.title as anime_title, a.code as anime_code
            FROM shorts s
            INNER JOIN anime a ON s.anime_id = a.id
            ORDER BY s.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def increment_views(short_id: int, user_id: int) -> bool:
        """Foydalanuvchi uchun unik ko'rishni saqlash va hisobni oshirish."""
        db = await Database.connect()
        try:
            # Unik ko'rishni qo'shishga urinamiz
            await db.execute(
                "INSERT INTO short_views (short_id, user_id) VALUES (?, ?)",
                (short_id, user_id)
            )
            # Agar muvaffaqiyatli bo'lsa (UNIQUE constraint buzilmasa), jami ko'rishni oshiramiz
            await db.execute(
                "UPDATE shorts SET views = views + 1 WHERE id = ?", (short_id,)
            )
            await db.commit()
            return True
        except Exception:
            # Allaqachon ko'rgan bo'lsa xatolik beradi, ignore qilamiz
            return False

    @staticmethod
    async def delete(short_id: int) -> None:
        """Delete a short clip by its ID."""
        db = await Database.connect()
        await db.execute("DELETE FROM shorts WHERE id = ?", (short_id,))
        await db.commit()

    @staticmethod
    async def get_count() -> int:
        """Return the total number of shorts."""
        db = await Database.connect()
        cursor = await db.execute("SELECT COUNT(*) as cnt FROM shorts")
        row = await cursor.fetchone()
        return row["cnt"] if row else 0
