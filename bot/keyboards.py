from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# --- USER ASOSIY MENU ---
def main_menu(lang="uz"):
    """Foydalanuvchi uchun asosiy menyu"""
    if lang == "ru":
        b_products = "🎒 Продукты"
        b_topup = "💳 Пополнить баланс"
        b_orders = "📦 Мои заказы"
        b_settings = "⚙️ Язык / Настройки"
    else:
        b_products = "🎒 Mahsulotlar"
        b_topup = "💳 Hisobni to'ldirish"
        b_orders = "📦 Buyurtmalarim"
        b_settings = "⚙️ Til / Sozlamalar"

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(b_products), KeyboardButton(b_topup)],
            [KeyboardButton(b_orders), KeyboardButton(b_settings)]
        ],
        resize_keyboard=True
    )
    return kb


# --- MAHSULOT TURLARI ---
def products_type_kb(lang="uz"):
    """Coin yoki Rank turini tanlash"""
    if lang == "ru":
        c1 = "Монеты"
        c2 = "Ранги"
    else:
        c1 = "Coin (coinlar)"
        c2 = "Rank (ranklar)"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(c1, callback_data="type_coin"),
                InlineKeyboardButton(c2, callback_data="type_rank")
            ]
        ]
    )
    return kb


# --- MAHSULOTLAR RO‘YXATI ---
def products_inline(products):
    """Mahsulotlarni InlineKeyboard shaklida chiqarish"""
    kb = InlineKeyboardMarkup()
    for p in products:
        kb.row(
            InlineKeyboardButton(
                f"{p['name']} — {p['price']} so'm",
                callback_data=f"buy_{p['code']}"
            )
        )
    return kb


# --- ADMIN TASDIQLASH TUGMALARI ---
def confirm_admin_kb():
    """Admin uchun tasdiqlash yoki rad etish"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("✅ Tasdiqlash / Approve", callback_data="admin_approve")],
            [InlineKeyboardButton("❌ Rad etish / Reject", callback_data="admin_reject")]
        ]
    )
    return kb


# --- ADMIN PANELI ---
def admin_menu():
    """Admin menyusi (InlineKeyboard)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("➕ Mahsulot qo‘shish", callback_data="add_product")],
            [InlineKeyboardButton("📦 Mahsulotlar ro‘yxati", callback_data="show_products")],
            [InlineKeyboardButton("💳 Pending to‘lovlar", callback_data="pending_topups")],
            [InlineKeyboardButton("🛍 Pending buyurtmalar", callback_data="pending_orders")],
            [InlineKeyboardButton("💰 Balansni o‘zgartirish", callback_data="edit_balance")],
            [InlineKeyboardButton("🚪 Chiqish", callback_data="exit_admin")]
        ]
    )
