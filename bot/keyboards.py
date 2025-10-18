from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


# --- USER ASOSIY MENU ---
def main_menu(lang: str = "uz") -> ReplyKeyboardMarkup:
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

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=b_products), KeyboardButton(text=b_topup)],
            [KeyboardButton(text=b_orders), KeyboardButton(text=b_settings)]
        ],
        resize_keyboard=True
    )


# --- MAHSULOT TURLARI ---
def products_type_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Coin yoki Rank turini tanlash"""
    if lang == "ru":
        c1 = "Монеты"
        c2 = "Ранги"
    else:
        c1 = "💰 Coin (coinlar)"
        c2 = "⭐ Rank (ranklar)"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=c1, callback_data="type_coin"),
                InlineKeyboardButton(text=c2, callback_data="type_rank")
            ]
        ]
    )


# --- MAHSULOTLAR RO‘YXATI ---
def products_inline(products: list) -> InlineKeyboardMarkup:
    """Mahsulotlarni InlineKeyboard shaklida chiqarish"""
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for p in products:
        name = p.get("name", "Noma'lum")
        price = p.get("price", 0)
        code = p.get("code", "none")
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{name} — {price} so'm",
                callback_data=f"buy_{code}"
            )
        ])
    return kb


# --- ADMIN TASDIQLASH TUGMALARI ---
def confirm_admin_kb() -> InlineKeyboardMarkup:
    """Admin uchun tasdiqlash yoki rad etish"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash / Approve", callback_data="admin_approve")],
            [InlineKeyboardButton(text="❌ Rad etish / Reject", callback_data="admin_reject")]
        ]
    )


# --- ADMIN PANELI ---
def admin_menu() -> InlineKeyboardMarkup:
    """Admin menyusi (InlineKeyboard)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Mahsulot qo‘shish", callback_data="add_product")],
            [InlineKeyboardButton(text="📦 Mahsulotlar ro‘yxati", callback_data="show_products")],
            [InlineKeyboardButton(text="💳 Pending to‘lovlar", callback_data="pending_topups")],
            [InlineKeyboardButton(text="🛍 Pending buyurtmalar", callback_data="pending_orders")],
            [InlineKeyboardButton(text="💰 Balansni o‘zgartirish", callback_data="edit_balance")],
            [InlineKeyboardButton(text="🚪 Chiqish", callback_data="exit_admin")]
        ]
    )
