"""
models/vip.py - VIP plans model with async CRUD operations.
Handles VIP plan creation, listing, and retrieval.
"""

from database import Database


class VipModel:
    """Provides async database operations for the vip_plans table."""

    @staticmethod
    async def create_plan(name: str, price: int, duration_days: int, card_number: str = "") -> int:
        """Create a new VIP plan and return its ID."""
        db = await Database.connect()
        cursor = await db.execute(
            "INSERT INTO vip_plans (name, price, duration_days, card_number) VALUES (?, ?, ?, ?)",
            (name, price, duration_days, card_number),
        )
        await db.commit()
        return cursor.lastrowid

    @staticmethod
    async def get_plan(plan_id: int) -> dict | None:
        """Fetch a VIP plan by its ID."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM vip_plans WHERE id = ?", (plan_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    async def get_all_plans() -> list[dict]:
        """Retrieve all available VIP plans."""
        db = await Database.connect()
        cursor = await db.execute("SELECT * FROM vip_plans ORDER BY price ASC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    async def update_plan(plan_id: int, **kwargs) -> None:
        """Update one or more fields of a VIP plan."""
        if not kwargs:
            return
        set_clause = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [plan_id]
        db = await Database.connect()
        await db.execute(f"UPDATE vip_plans SET {set_clause} WHERE id = ?", values)
        await db.commit()

    @staticmethod
    async def delete_plan(plan_id: int) -> None:
        """Delete a VIP plan by its ID."""
        db = await Database.connect()
        await db.execute("DELETE FROM vip_plans WHERE id = ?", (plan_id,))
        await db.commit()
