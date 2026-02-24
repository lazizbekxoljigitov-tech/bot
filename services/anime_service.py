"""
services/anime_service.py - Anime ma'lumotlarini formatlash xizmati.
Premium dizayn, emojilar va chiroyli tartib.
"""

from models.anime import AnimeModel
from models.episode import EpisodeModel


class AnimeService:
    """Anime bilan bog'liq matnlarni chiroyli formatlash."""

    @staticmethod
    async def get_anime_info_text(anime_id: int) -> str:
        """Anime haqida to'liq ma'lumot matnini yaratish."""
        anime = await AnimeModel.get_by_id(anime_id)
        if not anime:
            return "❌ Anime topilmadi."

        ep_count = await EpisodeModel.get_episode_count(anime_id)
        vip_status = "💎 VIP" if anime["is_vip"] else "🆓 Bepul"

        text = (
            f"<b>🎬 {anime['title']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"🎭 <b>Janr:</b> {anime['genre']}\n"
            f"🔢 <b>Qismlar:</b> {ep_count}/{anime['total_episodes']}\n"
            f"📅 <b>S/E:</b> {anime['season_count']} | {ep_count}\n"
            f"👁 <b>Ko'rilgan:</b> {anime['views']}\n"
            f"🛡 <b>Holati:</b> {vip_status}\n"
            f"🆔 <b>Kod:</b> <code>{anime['code']}</code>\n\n"
            f"📝 <b>Tavsif:</b>\n{anime['description']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Marhamat, tomosha qiling!</i>"
        )
        return text

    @staticmethod
    async def get_anime_card_text(anime: dict) -> str:
        """Qidiruv natijalari uchun qisqa matn."""
        vip_mark = "💎 " if anime["is_vip"] else ""
        return f"📺 {vip_mark}<b>{anime['title']}</b> ({anime['genre']})"

    @staticmethod
    async def format_episode_text(episode: dict, anime_title: str) -> str:
        """Qism videosi uchun caption matni."""
        vip_status = "💎 VIP" if episode["is_vip"] else "🆓 Bepul"
        text = (
            f"<b>🎬 {anime_title}</b>\n"
            f"🎞 <b>S{episode['season_number']} | E{episode['episode_number']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Nomi:</b> {episode['title'] or 'Nomsiz'}\n"
            f"🛡 <b>Holati:</b> {vip_status}\n"
            f"👁 <b>Ko'rishlar:</b> {episode['views']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🤖 @AnimeBot — eng sara animelar!"
        )
        return text

    @staticmethod
    def get_poster(anime: dict) -> str | None:
        """Anime posterini (file_id yoki URL) qaytarish."""
        return anime.get("poster_file_id") or anime.get("poster_url") or None
