"""
main.py - Botning asosiy kirish nuqtasi.
Ma'lumotlar bazasini yaratish, routerlarni ro'yxatdan o'tkazish,
middleware qo'shish va pollingni boshlash.
"""

import asyncio
import logging
import os
import sys

from config import LOG_DIR, LOG_FILE
from database import Database
from loader import bot, dp

# ---- Logging sozlash (file + console) ----
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def register_routers() -> None:
    """Barcha routerlarni dispatcherga ro'yxatdan o'tkazish."""
    from handlers.user.start import router as start_router
    from handlers.user.profile import router as profile_router
    from handlers.user.favorites import router as favorites_router
    from handlers.user.shorts import router as shorts_router
    from handlers.user.help import router as help_router
    from handlers.user.comments import router as comments_router
    from handlers.search.search import router as search_router
    from handlers.episodes.view import router as episodes_router
    from handlers.admin.anime_crud import router as anime_crud_router
    from handlers.admin.episode_crud import router as episode_crud_router
    from handlers.admin.vip_manage import router as vip_manage_router
    from handlers.admin.shorts_manage import router as shorts_manage_router
    from handlers.admin.stats import router as stats_router
    from handlers.admin.subscription import router as subscription_router
    from handlers.admin.dashboard import router as dashboard_router
    from handlers.admin.tools import router as admin_tools_router
    from handlers.vip.plans import router as vip_plans_router

    dp.include_routers(
        start_router,
        profile_router,
        favorites_router,
        shorts_router,
        help_router,
        comments_router,
        search_router,
        episodes_router,
        anime_crud_router,
        episode_crud_router,
        admin_tools_router,
        vip_manage_router,
        shorts_manage_router,
        stats_router,
        subscription_router,
        dashboard_router,
        broadcast_router,
        channel_post_router,
        vip_plans_router,
    )


def register_middlewares() -> None:
    """Middlewarelarni dispatcherga qo'shish."""
    from middlewares.logging_middleware import LoggingMiddleware
    from middlewares.throttling import ThrottlingMiddleware
    from middlewares.subscription import SubscriptionMiddleware
    from middlewares.maintenance import MaintenanceMiddleware

    dp.update.outer_middleware(LoggingMiddleware())
    dp.update.outer_middleware(MaintenanceMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(SubscriptionMiddleware())


async def on_startup() -> None:
    """Bot ishga tushganda bajariladigan funksiya."""
    logger.info("Ma'lumotlar bazasi yaratilmoqda...")
    await Database.create_tables()
    logger.info("Ma'lumotlar bazasi tayyor.")

    bot_info = await bot.get_me()
    logger.info("Bot ishga tushdi: @%s", bot_info.username)


async def on_shutdown() -> None:
    """Bot to'xtaganda bajariladigan funksiya."""
    logger.info("Bot to'xtatilmoqda...")
    await Database.close()
    await bot.session.close()
    logger.info("Bot to'xtatildi.")


async def main() -> None:
    """Asosiy funksiya - botni ishga tushirish."""
    register_routers()
    register_middlewares()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        logger.info("Polling boshlanmoqda...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.critical("Bot ishga tushishda xatolik: %s", str(e))
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")
    except Exception as e:
        logger.critical("Kutilmagan xatolik: %s", str(e))
