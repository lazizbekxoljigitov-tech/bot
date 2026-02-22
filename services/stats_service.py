"""
services/stats_service.py - Statistika biznes logikasi.
Admin paneli uchun statistik ma'lumotlarni tayyorlash.
"""

from models.stats import StatsModel


class StatsService:
    """Statistika bilan bog'liq biznes logika xizmati."""

    @staticmethod
    async def get_stats_text() -> str:
        """Admin uchun to'liq statistika matnini tayyorlash."""
        data = await StatsModel.get_overview()
        top = await StatsModel.get_top_anime(limit=5)

        text = (
            f"<b>\u25C8 Statistika</b>\n"
            f"\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n\n"
            f"\u25B8 <b>Foydalanuvchilar:</b> {data['total_users']}\n"
            f"\u25B8 <b>VIP foydalanuvchilar:</b> {data['vip_users']}\n"
            f"\u25B8 <b>Jami anime:</b> {data['total_anime']}\n"
            f"\u25B8 <b>Jami qismlar:</b> {data['total_episodes']}\n"
            f"\u25B8 <b>Jami ko'rishlar:</b> {data['total_views']}\n"
            f"\u25B8 <b>Jami shorts:</b> {data['total_shorts']}\n"
            f"\u25B8 <b>Jami izohlar:</b> {data['total_comments']}\n"
            f"\u25B8 <b>Jami sevimlilar:</b> {data['total_favorites']}\n"
        )

        if top:
            text += (
                f"\n<b>\u25B2 Top 5 Anime</b>\n"
                f"\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
            )
            for i, a in enumerate(top, 1):
                text += f"{i}. {a['title']} - {a['views']} ko'rish\n"

        return text
