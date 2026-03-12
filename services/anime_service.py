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
            f"⏳ <b>Holati:</b> {anime.get('status', 'Tugallangan')}\n"
            f"🎙 <b>Tarjima:</b> {anime.get('translator', 'AniBro')}\n"
            f"👁 <b>Ko'rilgan:</b> {anime['views']}\n"
            # f"🛡 <b>Holati:</b> {vip_status}\n" # Removed redundant status
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
    async def format_episode_text(episode: dict, anime: dict) -> str:
        """Qism videosi uchun caption matni (Premium)."""
        anime_title = anime.get('title', 'Noma''lum Anime')
        vip_status = "💎 VIP" if episode["is_vip"] else "Ozod"
        translator = anime.get('translator') or 'AniBro'
        
        text = (
            f"<b>{anime_title}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"◈ Qism: <b>{episode['episode_number']}</b>\n"
            f"◈ Tarjima: <b>{translator}</b>\n"
            f"◈ Kirish: <b>{vip_status}</b>\n"
            f"◈ Ko'rishlar: <b>{episode['views']}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🤖 @AnimeBot — eng sara animelar va qulayliklar!"
        )
        return text

    @staticmethod
    def get_poster(anime: dict) -> str | None:
        """Anime posterini (file_id yoki URL) qaytarish."""
        return anime.get("poster_file_id") or anime.get("poster_url") or None

    @staticmethod
    async def get_channel_post_text(anime_id: int) -> str:
        """Kanalga yuboriladigan katta post matni (Ultra Premium Box Layout)."""
        from config import NEWS_CHANNEL
        anime = await AnimeModel.get_by_id(anime_id)
        if not anime:
            return "❌ Anime topilmadi."

        ep_count = await EpisodeModel.get_episode_count(anime_id)
        status = anime.get('status') or 'Tugallangan'
        translator = anime.get('translator') or 'AniBro'
        
        text = (
            f"<b>{anime['title']}</b>\n"
            f"╭──────────────────────\n"
            f"├‣  <b>Holati:</b> {status}\n"
            f"├‣  <b>Anime:</b> {ep_count} Qism\n"
            f"├‣  <b>Tarjima:</b> {translator}\n"
            f"├‣  <b>Janrlari:</b> {anime['genre']}\n"
            f"├‣  <b>Kanal:</b> {NEWS_CHANNEL}\n"
            f"╰──────────────────────\n\n\n"
            f"✨ <i>Pastdagi tugmani bosing va tomosha qiling!</i>"
        )
        return text

    @staticmethod
    async def get_small_post_text(anime: dict) -> str:
        """Kanalga yuboriladigan kichik post matni (Box Layout)."""
        from config import NEWS_CHANNEL
        ep_count = await EpisodeModel.get_episode_count(anime['id'])
        status = anime.get('status') or 'Tugallangan'
        
        return (
            f"<b>{anime['title']}</b>\n"
            f"╭──────────────────────\n"
            f"├‣  <b>Holati:</b> {status}\n"
            f"├‣  <b>Qismlar:</b> {ep_count} ta\n"
            f"├‣  <b>Kanal:</b> {NEWS_CHANNEL}\n"
            f"╰──────────────────────"
        )
