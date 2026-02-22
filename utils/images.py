import re

def get_direct_url(url: str) -> str:
    """Google Drive share link-larini to'g'ridan-to'g'ri rasm linkiga aylantiradi."""
    if not url:
        return ""
        
    # Drive linklarini aniqlash
    if "drive.google.com" in url or "share.google" in url:
        doc_id = None
        # ... (rest of drive logic) ...
        # (Simplified for brevity in snippet, keeping existing logic)
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", url) or re.search(r"id=([a-zA-Z0-9_-]+)", url) or re.search(r"share\.google/([a-zA-Z0-9_-]+)", url)
        if match:
            return f"https://drive.google.com/uc?export=view&id={match.group(1)}"

    # ibb.co linklarini aniqlash
    if "ibb.co" in url and "i.ibb.co" not in url:
        # ibb.co/ID formatini aniqlash (bu odatda sahifa linki)
        # Eslatma: To'g'ridan-to'g'ri rasm linkini olish uchun i.ibb.co kerak
        # Agar foydalanuvchi sahifa linkini bersa, biz uni o'zgartira olmaymiz 
        # chunki rasm kengaytmasini (jpg/png) bilmaymiz.
        # Shunchaki return qilamiz va foydalanuvchiga 'Direct Link' olishni tavsiya qilamiz.
        pass
            
    return url

# Asosiy bo'limlar uchun rasmlar
_RAW_IMAGES = {
    "WELCOME": "https://ibb.co/99K7TpcL",
    "HELP": "https://ibb.co/gLq31sGw",
    "PROFILE": "https://ibb.co/Gf8TwfQh",
    "SEARCH": "https://ibb.co/HLBkHKYH",
    "VIP": "https://ibb.co/PzF93ZYj",
    "MAINTENANCE": "https://ibb.co/QFnxJTmK",
    "BROADCAST": "https://ibb.co/GQn00Kd4",
}

IMAGES = {k: get_direct_url(v) for k, v in _RAW_IMAGES.items()}

# DEBUG: Converted URLs
# for k, v in IMAGES.items():
#     print(f"DEBUG: {k} -> {v}")