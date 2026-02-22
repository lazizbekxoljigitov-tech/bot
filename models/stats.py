"""
models/stats.py - Statistics model.
Provides aggregated statistics for the admin dashboard.
"""

from database import Database


class StatsModel:
    """Provides aggregated statistics queries for the admin panel."""

    @staticmethod
    async def get_overview() -> dict:
        """Get an overview of all key metrics."""
        db = await Database.connect()

        # Total users
        cur = await db.execute("SELECT COUNT(*) as cnt FROM users")
        row = await cur.fetchone()
        total_users = row["cnt"] if row else 0

        # VIP users
        cur = await db.execute("SELECT COUNT(*) as cnt FROM users WHERE is_vip = 1")
        row = await cur.fetchone()
        vip_users = row["cnt"] if row else 0

        # Total anime
        cur = await db.execute("SELECT COUNT(*) as cnt FROM anime")
        row = await cur.fetchone()
        total_anime = row["cnt"] if row else 0

        # Total episodes
        cur = await db.execute("SELECT COUNT(*) as cnt FROM episodes")
        row = await cur.fetchone()
        total_episodes = row["cnt"] if row else 0

        # Total views (anime)
        cur = await db.execute("SELECT COALESCE(SUM(views), 0) as total FROM anime")
        row = await cur.fetchone()
        total_views = row["total"] if row else 0

        # Total shorts
        cur = await db.execute("SELECT COUNT(*) as cnt FROM shorts")
        row = await cur.fetchone()
        total_shorts = row["cnt"] if row else 0

        # Total comments
        cur = await db.execute("SELECT COUNT(*) as cnt FROM comments")
        row = await cur.fetchone()
        total_comments = row["cnt"] if row else 0

        # Total favorites
        cur = await db.execute("SELECT COUNT(*) as cnt FROM favorites")
        row = await cur.fetchone()
        total_favorites = row["cnt"] if row else 0

        return {
            "total_users": total_users,
            "vip_users": vip_users,
            "total_anime": total_anime,
            "total_episodes": total_episodes,
            "total_views": total_views,
            "total_shorts": total_shorts,
            "total_comments": total_comments,
            "total_favorites": total_favorites,
        }

    @staticmethod
    async def get_top_anime(limit: int = 5) -> list[dict]:
        """Get top anime by views for the stats dashboard."""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT title, views FROM anime ORDER BY views DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
