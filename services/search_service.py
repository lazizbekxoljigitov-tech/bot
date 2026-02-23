"""
services/search_service.py - Qidiruv biznes logikasi.
Turli qidiruv turlarini boshqarish va natijalarni formatlash.
"""

import math
from models.anime import AnimeModel
from config import SEARCH_RESULTS_PER_PAGE


class SearchService:
    """Qidiruv bilan bog'liq biznes logika xizmati."""

    @staticmethod
    async def search_by_title(query: str, page: int = 0) -> tuple[list[dict], int]:
        """Nom bo'yicha qidirish. Returns (results, total_pages)."""
        all_results = await AnimeModel.search_by_title(query, limit=100)
        return SearchService._paginate(all_results, page)

    @staticmethod
    async def search_by_genre(genre: str, page: int = 0) -> tuple[list[dict], int]:
        """Janr bo'yicha qidirish. Returns (results, total_pages)."""
        all_results = await AnimeModel.search_by_genre(genre, limit=100)
        return SearchService._paginate(all_results, page)

    @staticmethod
    async def search_by_code(code: str) -> dict | None:
        """Kod bo'yicha qidirish. Returns single anime or None."""
        return await AnimeModel.get_by_code(code)

    @staticmethod
    async def get_top_anime(page: int = 0) -> tuple[list[dict], int]:
        """Eng ko'p ko'rilgan animelar. Returns (results, total_pages)."""
        all_results = await AnimeModel.get_top(limit=50)
        return SearchService._paginate(all_results, page)

    @staticmethod
    async def get_latest_anime(page: int = 0) -> tuple[list[dict], int]:
        """Yangi qo'shilgan animelar. Returns (results, total_pages)."""
        all_results = await AnimeModel.get_latest(limit=50)
        return SearchService._paginate(all_results, page)

    @staticmethod
    async def get_vip_anime(page: int = 0) -> tuple[list[dict], int]:
        """VIP animelar. Returns (results, total_pages)."""
        all_results = await AnimeModel.get_vip_anime(limit=50)
        return SearchService._paginate(all_results, page)

    @staticmethod
    def _paginate(items: list[dict], page: int) -> tuple[list[dict], int]:
        """Ro'yxatni sahifalarga bo'lish."""
        total = len(items)
        total_pages = max(1, math.ceil(total / SEARCH_RESULTS_PER_PAGE))
        start = page * SEARCH_RESULTS_PER_PAGE
        end = start + SEARCH_RESULTS_PER_PAGE
        return items[start:end], total_pages

    @staticmethod
    async def get_random_anime() -> dict | None:
        """Tasodifiy anime olish."""
        results = await AnimeModel.get_random(limit=1)
        return results[0] if results else None

