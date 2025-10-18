import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# --- Asosiy sozlamalar ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8317966549:AAEIb0v6tnLMjkb5wc7Iw-XscOJg8mj9wEM").strip()
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN .env faylida topilmadi. Iltimos, .env ni to‘ldiring.")

# --- Admin va bot ma'lumotlari ---
# OWNER_CHAT_ID ni xavfsiz tarzda olish (intga o‘tmasa xato bermaydi)
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID", "993523630")
try:
    OWNER_CHAT_ID = int(OWNER_CHAT_ID)
except ValueError:
    OWNER_CHAT_ID = None

# Asosiy adminlar ro‘yxati
ADMINS = [int(x) for x in os.getenv("ADMINS", "993523630").split(",") if x.strip().isdigit()]

# Boshqa admin ID'lar (ixtiyoriy)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "993523630").split(",") if x.strip().isdigit()]

# ADMIN_IDS + ADMINS ni birlashtiramiz (duplicatelarsiz)
ALL_ADMINS = list(set(ADMINS + ADMIN_IDS))
if OWNER_CHAT_ID and OWNER_CHAT_ID not in ALL_ADMINS:
    ALL_ADMINS.append(OWNER_CHAT_ID)

# --- Boshqa sozlamalar ---
ADMIN_CARD = os.getenv("ADMIN_CARD", "5614 5890 1255 9864 (John Doe)")
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "uz")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@mr1kevin")
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000/api/")
COIN_PRICE = int(os.getenv("COIN_PRICE", "1000"))

# --- Konsolga qisqa ma’lumot ---
print(f"✅ Bot yuklandi: OWNER_CHAT_ID={OWNER_CHAT_ID}, ADMINS={ALL_ADMINS}")
