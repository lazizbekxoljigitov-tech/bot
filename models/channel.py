"""
models/channel.py - Channel model with async CRUD operations.
Handles forced subscription channel management.
"""

from database import Database


class ChannelModel:
    """Provides async database operations for the channels table."""

    @staticmethod
    async def add(channel_id: str, channel_link: str) -> int:
        """Add a new channel for forced subscription. Returns the record ID."""
        db = await Database.connect()
        cursor = await db.execute(
            "INSERT OR IGNORE INTO channels (channel_id, channel_link) VALUES (?, ?)",
            (channel_id, channel_link),
        )
        await db.commit()
        return cursor.lastrowid

    @staticmethod
    async def remove(channel_id: str) -> None:
        """Remove a channel from forced subscription list."""
        db = await Database.connect()
        await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
        await db.commit()

    @staticmethod
    async def get_all() -> list[dict]:
        """Retrieve all forced subscription channels."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM channels ORDER BY added_at DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def get_by_channel_id(channel_id: str) -> dict | None:
        """Fetch a channel record by its Telegram channel ID."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM channels WHERE channel_id = ?", (channel_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
