"""
models/anime.py - Anime model with async CRUD operations.
Handles anime creation, editing, deletion, search, and view counting.
"""

from database import Database


class AnimeModel:
    """Provides async database operations for the anime table."""

    @staticmethod
    async def create(
        title: str,
        code: str,
        description: str,
        genre: str,
        season_count: int,
        total_episodes: int,
        poster_file_id: str = "",
        poster_url: str = "",
        is_vip: int = 0,
    ) -> int:
        """Insert a new anime record and return its ID."""
        db = await Database.connect()
        cursor = await db.execute(
            """
            INSERT INTO anime (title, code, description, genre, season_count,
                               total_episodes, poster_file_id, poster_url, is_vip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, code, description, genre, season_count, total_episodes, poster_file_id, poster_url, is_vip),
        )
        await db.commit()
        return cursor.lastrowid

    @staticmethod
    async def get_by_id(anime_id: int) -> dict | None:
        """Fetch an anime by its internal ID."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM anime WHERE id = ?", (anime_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    async def get_by_code(code: str) -> dict | None:
        """Fetch an anime by its unique code."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM anime WHERE code = ?", (code,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    async def update(anime_id: int, **kwargs) -> None:
        """Update one or more fields of an anime record."""
        if not kwargs:
            return
        set_clause = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [anime_id]
        db = await Database.connect()
        await db.execute(f"UPDATE anime SET {set_clause} WHERE id = ?", values)
        await db.commit()

    @staticmethod
    async def delete(anime_id: int) -> None:
        """Delete an anime record by its ID."""
        db = await Database.connect()
        await db.execute("DELETE FROM anime WHERE id = ?", (anime_id,))
        await db.commit()

    @staticmethod
    async def increment_views(anime_id: int) -> None:
        """Increment the view count of an anime by 1."""
        db = await Database.connect()
        await db.execute("UPDATE anime SET views = views + 1 WHERE id = ?", (anime_id,))
        await db.commit()

    @staticmethod
    async def search_by_title(query: str, limit: int = 20) -> list[dict]:
        """Search anime by title using LIKE pattern matching."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM anime WHERE title LIKE ? ORDER BY views DESC LIMIT ?",
            (f"%{query}%", limit),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def search_by_genre(genre: str, limit: int = 20) -> list[dict]:
        """Search anime by genre using LIKE pattern matching."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM anime WHERE genre LIKE ? ORDER BY views DESC LIMIT ?",
            (f"%{genre}%", limit),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def get_top(limit: int = 10) -> list[dict]:
        """Get the most viewed anime."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM anime ORDER BY views DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def get_latest(limit: int = 10) -> list[dict]:
        """Get the most recently added anime."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM anime ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def get_vip_anime(limit: int = 20) -> list[dict]:
        """Get all VIP-exclusive anime."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM anime WHERE is_vip = 1 ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def get_all(limit: int = 100, offset: int = 0) -> list[dict]:
        """Get all anime with pagination."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM anime ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def get_count() -> int:
        """Return the total number of anime records."""
        db = await Database.connect()
        cursor = await db.execute("SELECT COUNT(*) as cnt FROM anime")
        row = await cursor.fetchone()
        return row["cnt"] if row else 0
