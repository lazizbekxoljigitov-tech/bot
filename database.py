"""
database.py - Database initialization and connection management.
Creates all tables on startup using aiosqlite.
"""

import aiosqlite
import os
from config import DB_PATH


class Database:
    """Manages SQLite database connection and schema creation."""

    _connection: aiosqlite.Connection | None = None

    @classmethod
    async def connect(cls) -> aiosqlite.Connection:
        """Open a persistent database connection."""
        if cls._connection is None:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            cls._connection = await aiosqlite.connect(DB_PATH)
            cls._connection.row_factory = aiosqlite.Row
            await cls._connection.execute("PRAGMA journal_mode=WAL;")
            await cls._connection.execute("PRAGMA foreign_keys=ON;")
        return cls._connection

    @classmethod
    async def close(cls) -> None:
        """Close the database connection."""
        if cls._connection is not None:
            await cls._connection.close()
            cls._connection = None

    @classmethod
    async def create_tables(cls) -> None:
        """Create all tables if they do not exist."""
        db = await cls.connect()

        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT NOT NULL DEFAULT '',
                username TEXT DEFAULT '',
                is_vip INTEGER NOT NULL DEFAULT 0,
                vip_expire_date TEXT DEFAULT NULL,
                joined_date TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS anime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                description TEXT DEFAULT '',
                genre TEXT DEFAULT '',
                season_count INTEGER NOT NULL DEFAULT 1,
                total_episodes INTEGER NOT NULL DEFAULT 0,
                poster_file_id TEXT DEFAULT '',
                poster_url TEXT DEFAULT '',
                is_vip INTEGER NOT NULL DEFAULT 0,
                views INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER NOT NULL,
                season_number INTEGER NOT NULL DEFAULT 1,
                episode_number INTEGER NOT NULL,
                title TEXT DEFAULT '',
                video_file_id TEXT NOT NULL,
                is_vip INTEGER NOT NULL DEFAULT 0,
                views INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                anime_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE,
                UNIQUE(user_id, anime_id)
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                anime_id INTEGER NOT NULL,
                comment_text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT UNIQUE NOT NULL,
                channel_link TEXT NOT NULL DEFAULT '',
                added_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS vip_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                duration_days INTEGER NOT NULL,
                card_number TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT DEFAULT '',
                role TEXT DEFAULT 'admin',
                added_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS shorts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER NOT NULL,
                short_video_file_id TEXT NOT NULL,
                views INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS short_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                viewed_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (short_id) REFERENCES shorts(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(short_id, user_id)
            );

            CREATE INDEX IF NOT EXISTS idx_anime_code ON anime(code);
            CREATE INDEX IF NOT EXISTS idx_anime_genre ON anime(genre);
            CREATE INDEX IF NOT EXISTS idx_anime_views ON anime(views DESC);
            CREATE INDEX IF NOT EXISTS idx_anime_created ON anime(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_episodes_anime ON episodes(anime_id);
            CREATE INDEX IF NOT EXISTS idx_episodes_views ON episodes(views DESC);
            CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);
            CREATE INDEX IF NOT EXISTS idx_comments_anime ON comments(anime_id);
            CREATE INDEX IF NOT EXISTS idx_shorts_anime ON shorts(anime_id);
            CREATE INDEX IF NOT EXISTS idx_shorts_views ON shorts(views DESC);
            CREATE INDEX IF NOT EXISTS idx_short_views_short ON short_views(short_id);
            CREATE INDEX IF NOT EXISTS idx_users_joined ON users(joined_date DESC);
        """)


        await db.commit()
        await cls.migrate_database()

    @classmethod
    async def migrate_database(cls) -> None:
        """Apply schema migrations (e.g., adding missing columns)."""
        db = await cls.connect()
        
        # Add poster_url to anime table if it doesn't exist
        try:
            # Check if column exists by trying to select it
            await db.execute("SELECT poster_url FROM anime LIMIT 1")
        except Exception:
            # Column likely doesn't exist, add it
            print("Migrating: Adding poster_url column to anime table...")
            await db.execute("ALTER TABLE anime ADD COLUMN poster_url TEXT DEFAULT ''")
            await db.commit()
            print("Migration successful: poster_url added.")
        
        # You can add more migrations here as the schema evolves

