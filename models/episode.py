"""
models/episode.py - Episode model with async CRUD operations.
Handles episode creation, editing, deletion, and retrieval with pagination.
"""

from database import Database


class EpisodeModel:
    """Provides async database operations for the episodes table."""

    @staticmethod
    async def create(
        anime_id: int,
        season_number: int,
        episode_number: int,
        title: str,
        video_file_id: str,
        is_vip: int = 0,
    ) -> int:
        """Insert a new episode record and return its ID."""
        db = await Database.connect()
        cursor = await db.execute(
            """
            INSERT INTO episodes (anime_id, season_number, episode_number, title, video_file_id, is_vip)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (anime_id, season_number, episode_number, title, video_file_id, is_vip),
        )
        await db.commit()
        return cursor.lastrowid

    @staticmethod
    async def get_by_id(episode_id: int) -> dict | None:
        """Fetch an episode by its internal ID."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    async def get_seasons(anime_id: int) -> list[int]:
        """Get a sorted list of distinct season numbers for an anime."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT DISTINCT season_number FROM episodes WHERE anime_id = ? ORDER BY season_number",
            (anime_id,),
        )
        rows = await cursor.fetchall()
        return [row["season_number"] for row in rows]

    @staticmethod
    async def get_by_season(
        anime_id: int, season_number: int, limit: int = 50, offset: int = 0
    ) -> list[dict]:
        """Get episodes for a specific anime season with pagination."""
        db = await Database.connect()
        cursor = await db.execute(
            """
            SELECT * FROM episodes
            WHERE anime_id = ? AND season_number = ?
            ORDER BY episode_number ASC
            LIMIT ? OFFSET ?
            """,
            (anime_id, season_number, limit, offset),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def get_episode_count(anime_id: int, season_number: int | None = None) -> int:
        """Count episodes for an anime, optionally filtered by season."""
        db = await Database.connect()
        if season_number is not None:
            cursor = await db.execute(
                "SELECT COUNT(*) as cnt FROM episodes WHERE anime_id = ? AND season_number = ?",
                (anime_id, season_number),
            )
        else:
            cursor = await db.execute(
                "SELECT COUNT(*) as cnt FROM episodes WHERE anime_id = ?", (anime_id,)
            )
        row = await cursor.fetchone()
        return row["cnt"] if row else 0

    @staticmethod
    async def update(episode_id: int, **kwargs) -> None:
        """Update one or more fields of an episode record."""
        if not kwargs:
            return
        set_clause = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [episode_id]
        db = await Database.connect()
        await db.execute(f"UPDATE episodes SET {set_clause} WHERE id = ?", values)
        await db.commit()

    @staticmethod
    async def delete(episode_id: int) -> None:
        """Delete an episode by its ID."""
        db = await Database.connect()
        await db.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
        await db.commit()

    @staticmethod
    async def increment_views(episode_id: int) -> None:
        """Increment the view count of an episode by 1."""
        db = await Database.connect()
        await db.execute(
            "UPDATE episodes SET views = views + 1 WHERE id = ?", (episode_id,)
        )
        await db.commit()

    @staticmethod
    async def get_all_for_anime(anime_id: int) -> list[dict]:
        """Get all episodes for an anime ordered by season and episode number."""
        db = await Database.connect()
        cursor = await db.execute(
            """
            SELECT * FROM episodes WHERE anime_id = ?
            ORDER BY season_number ASC, episode_number ASC
            """,
            (anime_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
