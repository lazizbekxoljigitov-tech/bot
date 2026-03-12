"""
keyboards/inline.py - Inline klaviatura tugmalari.
Anime ko'rish, navigatsiya, pagination va VIP uchun premium dizayn.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ==============================================================
# ANIME KO'RISH TUGMALARI
# ==============================================================

def anime_view_keyboard(anime_id: int, is_favorite: bool = False) -> InlineKeyboardMarkup:
    """Anime ko'rish sahifasidagi premium inline tugmalar."""
    builder = InlineKeyboardBuilder()
    
    # Row 1: Primary action
    builder.row(InlineKeyboardButton(text="▶️ Tomosha qilish", callback_data=f"watch:{anime_id}"))
    
    # Row 2: Secondary actions
    fav_text = "⭐ Sevimlilarda" if is_favorite else "➕ Sevimlilarga"
    fav_action = "unfav" if is_favorite else "fav"
    builder.row(
        InlineKeyboardButton(text=fav_text, callback_data=f"{fav_action}:{anime_id}"),
        InlineKeyboardButton(text="🔗 Ulashish", switch_inline_query=f"anime_{anime_id}")
    )
    
    # Row 3: Community
    builder.row(
        InlineKeyboardButton(text="✍️ Izohlar", callback_data=f"comments_list:{anime_id}:0"),
        InlineKeyboardButton(text="💬 Fikr bildirish", callback_data=f"comment:{anime_id}")
    )
    
    # Row 4: Navigation
    builder.row(InlineKeyboardButton(text="⬅️ Bosh sahifa", callback_data="back_to_menu"))
    
    return builder.as_markup()


# ==============================================================
# SEZONLAR RO'YXATI
# ==============================================================

def seasons_keyboard(anime_id: int, seasons: list[int]) -> InlineKeyboardMarkup:
    """Anime sezonlari ro'yxati tugmalari."""
    builder = InlineKeyboardBuilder()
    for s in seasons:
        builder.button(text=f"{s}-sezon", callback_data=f"season:{anime_id}:{s}:0")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"anime_details:{anime_id}"))
    return builder.as_markup()


# ==============================================================
# QISMLAR RO'YXATI (PAGINATION)
# ==============================================================

def episodes_keyboard(
    anime_id: int,
    season: int,
    episodes: list[dict],
    page: int,
    total_pages: int,
    is_single_season: bool = False,
) -> InlineKeyboardMarkup:
    """Qismlar ro'yxati va pagination tugmalari (Ixcham)."""
    builder = InlineKeyboardBuilder()

    # 4 tadan qilib taxlaymiz - juda qulay
    for ep in episodes:
        builder.button(
            text=f"{ep['episode_number']}",
            callback_data=f"episode:{ep['id']}",
        )
    builder.adjust(4)

    # Paginatsiya
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"season:{anime_id}:{season}:{page - 1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"season:{anime_id}:{season}:{page + 1}"))

    if len(nav_buttons) > 1:
        builder.row(*nav_buttons)

    # Orqaga
    back_text = "⬅️ Orqaga"
    back_callback = f"anime_details:{anime_id}" if is_single_season else f"watch:{anime_id}"
    builder.row(InlineKeyboardButton(text=back_text, callback_data=back_callback))

    return builder.as_markup()


# ==============================================================
# QISM KO'RISH TUGMALARI
# ==============================================================

def episode_view_keyboard(anime_id: int, episode_id: int) -> InlineKeyboardMarkup:
    """Video ko'p ko'rilayotganda qulay navigatsiya."""
    builder = InlineKeyboardBuilder()
    
    # Row 1: Listga qaytish
    builder.row(InlineKeyboardButton(text="📁 Barcha qismlar", callback_data=f"watch:{anime_id}"))
    
    # Row 2: Secondary
    builder.row(
        InlineKeyboardButton(text="🏠 Anime sahifasi", callback_data=f"anime_details:{anime_id}"),
        InlineKeyboardButton(text="🚀 Ulashish", switch_inline_query=f"anime_{anime_id}")
    )
    
    return builder.as_markup()


# ==============================================================
# QIDIRUV NATIJALARI
# ==============================================================

def search_results_keyboard(
    results: list[dict], page: int, total_pages: int, query_type: str, query_val: str
) -> InlineKeyboardMarkup:
    """Qidiruv natijalari va pagination tugmalari."""
    builder = InlineKeyboardBuilder()

    for anime in results:
        builder.button(
            text=f"📺 {anime['title']}",
            callback_data=f"anime_details:{anime['id']}",
        )

    builder.adjust(1)

    # Pagination
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"search_page:{query_type}:{query_val}:{page - 1}",
            )
        )
    if total_pages > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text=f"📄 {page + 1}/{total_pages}",
                callback_data="noop",
            )
        )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"search_page:{query_type}:{query_val}:{page + 1}",
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()


# ==============================================================
# SEVIMLILAR RO'YXATI
# ==============================================================

def favorites_keyboard(favorites: list[dict]) -> InlineKeyboardMarkup:
    """Foydalanuvchi sevimlilari ro'yxati."""
    builder = InlineKeyboardBuilder()
    for anime in favorites:
        builder.button(
            text=f"⭐️ {anime['title']}",
            callback_data=f"anime:{anime['id']}",
        )
    builder.adjust(1)
    if not favorites:
        builder.button(
            text="🔍 Anime qidirish",
            callback_data="open_search",
        )
    return builder.as_markup()


# ==============================================================
# SHORTS TUGMALARI
# ==============================================================

def shorts_keyboard(short_id: int, anime_id: int, index: int, total: int) -> InlineKeyboardMarkup:
    """Shorts navigatsiya tugmalari."""
    buttons = []

    # Navigation row
    nav = []
    if index > 0:
        nav.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"short_nav:{index - 1}",
            )
        )
    nav.append(
        InlineKeyboardButton(
            text=f"🔢 {index + 1}/{total}",
            callback_data="noop",
        )
    )
    if index < total - 1:
        nav.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"short_nav:{index + 1}",
            )
        )
    buttons.append(nav)

    buttons.append([
        InlineKeyboardButton(
            text="📺 To'liq anime",
            callback_data=f"anime:{anime_id}",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==============================================================
# VIP TUGMALARI
# ==============================================================

def vip_plans_keyboard(plans: list[dict], is_vip: bool = False, anime_title: str | None = None) -> InlineKeyboardMarkup:
    """VIP rejalar ro'yxati (Faqat nomlar)."""
    builder = InlineKeyboardBuilder()
    for plan in plans:
        # Agar anime_title bo'lsa, tugmada o'sha anime nomini ko'rsatamiz
        text = anime_title if anime_title else plan['name']
        builder.button(
            text=f"💎 {text}",
            callback_data=f"vip_details:{plan['id']}",
        )
    builder.adjust(1)
    
    if is_vip:
        builder.row(
            InlineKeyboardButton(text="🎖 VIP Qo'llab-quvvatlash", url="https://t.me/DEV_BR0")
        )
        builder.row(
            InlineKeyboardButton(text="🎁 Eksklyuziv animelar", callback_data="search_page:vip:all:0")
        )
        
    builder.row(
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_menu")
    )
    return builder.as_markup()


def vip_details_keyboard(plan: dict) -> InlineKeyboardMarkup:
    """Reja tafsilotlari (To'lovga o'tish tugmasi bilan)."""
    builder = InlineKeyboardBuilder()
    
    # Narx tugmasi endi to'lovga o'tkazadi
    builder.button(
        text=f"💰 {plan['price']} so'm | ⏳ {plan['duration_days']} kun",
        callback_data=f"vip_plan:{plan['id']}"
    )
    builder.button(
        text="⬅️ Orqaga",
        callback_data="vip_plans_back"
    )
    
    builder.adjust(1)
    return builder.as_markup()


def vip_payment_keyboard(plan_id: int) -> InlineKeyboardMarkup:
    """VIP to'lov tasdiqlash."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Screenshot yubordim",
                    callback_data=f"vip_paid:{plan_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data="back_to_menu",
                ),
            ],
        ]
    )


def vip_admin_approve_keyboard(user_tg_id: int, plan_id: int) -> InlineKeyboardMarkup:
    """Admin uchun VIP tasdiqlash."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"vip_approve:{user_tg_id}:{plan_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"vip_reject:{user_tg_id}",
                ),
            ],
        ]
    )


# ==============================================================
# MAJBURIY OBUNA
# ==============================================================

def subscription_keyboard(channels: list[dict]) -> InlineKeyboardMarkup:
    """Majburiy obuna kanallari."""
    builder = InlineKeyboardBuilder()
    for ch in channels:
        name = ch.get("channel_name") or "Kanalga o'tish"
        builder.button(
            text=f"📢 {name}",
            url=ch["channel_link"],
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(
            text="✅ Tekshirish",
            callback_data="check_subscription",
        )
    )
    return builder.as_markup()


def admin_channels_keyboard(channels: list[dict]) -> InlineKeyboardMarkup:
    """Admin uchun kanallarni o'chirish klaviaturasi."""
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.button(
            text=f"❌ {ch['channel_name']}",
            callback_data=f"del_channel:{ch['channel_id']}",
        )
    builder.adjust(1)
    return builder.as_markup()


# ==============================================================
# ADMIN: ANIME TANLASH
# ==============================================================

def anime_select_keyboard(anime_list: list[dict], action: str) -> InlineKeyboardMarkup:
    """Admin uchun anime tanlash."""
    builder = InlineKeyboardBuilder()
    for a in anime_list:
        builder.button(
            text=f"📺 {a['title']} [{a['code']}]",
            callback_data=f"{action}:{a['id']}",
        )
    builder.adjust(1)
    return builder.as_markup()


# ==============================================================
# IZOHLAR RO'YXATI
# ==============================================================

def comments_list_keyboard(
    anime_id: int, page: int, total_pages: int
) -> InlineKeyboardMarkup:
    """Izohlar pagination."""
    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"comments_list:{anime_id}:{page - 1}",
            )
        )
    if total_pages > 1:
        nav.append(
            InlineKeyboardButton(
                text=f"📄 {page + 1}/{total_pages}",
                callback_data="noop",
            )
        )
    if page < total_pages - 1:
        nav.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"comments_list:{anime_id}:{page + 1}",
            )
        )

    buttons = []
    if nav:
        buttons.append(nav)
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data=f"anime:{anime_id}",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==============================================================
# KANAL POST TUGMALARI
# ==============================================================

def channel_post_keyboard(anime_id: int, bot_username: str) -> InlineKeyboardMarkup:
    """Kichik post uchun tugma (botga havola)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="▶️ Tomosha qilish",
                    url=f"https://t.me/{bot_username}?start=anime_{anime_id}",
                ),
            ]
        ]
    )


def channel_big_post_keyboard(anime_id: int, bot_username: str) -> InlineKeyboardMarkup:
    """Katta post uchun tugmalar (Premium & Compact)."""
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text="▶️ Tomosha qilish", url=f"https://t.me/{bot_username}?start=anime_{anime_id}"))
    
    builder.row(
        InlineKeyboardButton(text="⭐ Sevimlilar", url=f"https://t.me/{bot_username}?start=fav_{anime_id}"),
        InlineKeyboardButton(text="🤖 Botga o'tish", url=f"https://t.me/{bot_username}")
    )
    
    return builder.as_markup()
# ==============================================================
# ADMIN DASHBOARD KEYBOARDS
# ==============================================================

def admin_dashboard_keyboard() -> InlineKeyboardMarkup:
    """Asosiy admin paneli (dashboard) uchun klaviatura."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="⚙️ Bot Sozlamalari", callback_data="admin_settings")
    builder.button(text="👥 Adminlar Boshqaruvi", callback_data="admin_admins")
    builder.button(text="📊 Statistika", callback_data="admin_stats")
    builder.button(text="📤 Xabar yuborish", callback_data="admin_broadcast")
    
    builder.adjust(2)
    return builder.as_markup()


def admin_settings_keyboard(maintenance: str) -> InlineKeyboardMarkup:
    """Bot sozlamalari menyusi."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🙋‍♂️ Support Havolasi", callback_data="set_setting:support_link")
    builder.button(text="📢 Kanal Havolasi", callback_data="set_setting:news_channel")
    
    m_text = "🟢 Texnik ishlar: ON" if maintenance == "ON" else "🔴 Texnik ishlar: OFF"
    builder.button(text=m_text, callback_data="toggle_maintenance")
    
    builder.button(text="💳 Karta Raqami", callback_data="set_setting:vip_card_number")
    builder.button(text="👤 Karta Egasi (Ism)", callback_data="set_setting:vip_card_name")
    
    builder.button(text="⬅️ Orqaga", callback_data="admin_dashboard")
    
    builder.adjust(1)
    return builder.as_markup()


def admin_manage_keyboard(admins: list) -> InlineKeyboardMarkup:
    """Adminlarni boshqarish menyusi."""
    builder = InlineKeyboardBuilder()
    
    for a in admins:
        builder.button(
            text=f"👤 {a['full_name']} ({a['role']})", 
            callback_data=f"view_admin:{a['telegram_id']}"
        )
    
    builder.button(text="➕ Yangi Admin", callback_data="add_new_admin")
    builder.button(text="⬅️ Orqaga", callback_data="admin_dashboard")
    
    builder.adjust(1)
    return builder.as_markup()


def admin_action_keyboard(admin_id: int) -> InlineKeyboardMarkup:
    """Tanlangan admin uchun amallar."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="❌ Adminlikdan olish", callback_data=f"delete_admin:{admin_id}")
    builder.button(text="⬅️ Orqaga", callback_data="admin_admins")
    
    builder.adjust(1)
    return builder.as_markup()
# ==============================================================
# ADMIN: SHORTS VA MEDIA FIX
# ==============================================================

def admin_fix_media_keyboard(context_info: str, media_type: str) -> InlineKeyboardMarkup:
    """Admin alerti uchun 'To'g'rilash' tugmasi."""
    builder = InlineKeyboardBuilder()
    
    # Context info dan ID ni qidirib ko'ramiz (masalan: "Shorts: naruto (ID: 1)")
    import re
    match = re.search(r"ID: (\d+)", context_info)
    
    if match:
        obj_id = match.group(1)
        if "Shorts" in context_info:
            builder.button(text="🔧 Videoni yangilash", callback_data=f"fix_short:{obj_id}")
        elif "Anime" in context_info:
            builder.button(text="🖼 Posterni yangilash", callback_data=f"fix_anime_poster:{obj_id}")
        elif "Episode" in context_info:
            builder.button(text="🎞 Videoni yangilash", callback_data=f"fix_ep_video:{obj_id}")
            
    builder.button(text="🛠 Dashboard", callback_data="admin_dashboard")
    builder.adjust(1)
    return builder.as_markup()


def shorts_manage_keyboard(shorts: list[dict]) -> InlineKeyboardMarkup:
    """Shorts boshqarish ro'yxati."""
    builder = InlineKeyboardBuilder()
    for s in shorts:
        builder.button(
            text=f"🎬 {s['anime_title']} (ID: {s['id']})",
            callback_data=f"manage_short:{s['id']}"
        )
    
    builder.button(text="➕ Yangi Shorts", callback_data="add_short_direct")
    builder.button(text="⬅️ Orqaga", callback_data="admin_dashboard")
    builder.adjust(1)
    return builder.as_markup()


def short_action_keyboard(short_id: int) -> InlineKeyboardMarkup:
    """Tanlangan short uchun amallar."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Videoni yangilash", callback_data=f"edit_short_video:{short_id}")
    builder.button(text="❌ O'chirish", callback_data=f"delete_short_confirm:{short_id}")
    builder.button(text="⬅️ Orqaga", callback_data="admin_manage_shorts")
    builder.adjust(1)
    return builder.as_markup()
