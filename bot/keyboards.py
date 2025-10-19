from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)

# Til tanlash (reply keyboard)
def choose_language_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O‘zbekcha"), KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return kb

# Asosiy menu
def main_menu(lang: str = "uz"):
    if lang == "uz":
        buttons = [
            [KeyboardButton(text="🎒 Mahsulotlar")],
            [KeyboardButton(text="💳 Hisobni to'ldirish")],
            [KeyboardButton(text="🛒 Buyurtmalarim")],
            [KeyboardButton(text="💰 Mening balansim")],
            [KeyboardButton(text="⚙️ Til / Sozlamalar")]
        ]
    else:
        buttons = [
            [KeyboardButton(text="🎒 Продукты")],
            [KeyboardButton(text="💳 Пополнить счет")],
            [KeyboardButton(text="🛒 Мои заказы")],
            [KeyboardButton(text="💰 Мой баланс")],
            [KeyboardButton(text="⚙️ Язык / Настройки")]
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Mahsulot turlari (inline)
def products_type_kb(lang: str = "uz"):
    if lang == "ru":
        c1, c2 = "Монеты", "Ранги"
    else:
        c1, c2 = "💰 Coin (coinlar)", "⭐ Rank (ranklar)"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=c1, callback_data="type_coin"),
         InlineKeyboardButton(text=c2, callback_data="type_rank")]
    ])

# Products inline list (dynamik)
def products_inline(products):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for p in products:
        kb.inline_keyboard.append(
            [InlineKeyboardButton(text=f"{p['name']} — {p['price']:,} so'm", callback_data=f"buy_{p['code']}")]
        )
    return kb


def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pending Top-ups", callback_data="admin:pending_topups")],
        [InlineKeyboardButton(text="🛒 Pending Orders", callback_data="admin:pending_orders")],
        [InlineKeyboardButton(text="📦 Manage Products", callback_data="admin:products")],
        [InlineKeyboardButton(text="👥 Users", callback_data="admin:users")],
    ])


# ===================== PRODUCT MENU =====================

def product_menu(products):
    buttons = []
    for p in products:
        buttons.append([InlineKeyboardButton(text=f"{p['name']} — {p['price']:,} so‘m", callback_data=f"product_{p['code']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ===================== PAYMENT =====================


def confirm_admin_kb(pid: int = 0, type_: str = "topup") -> InlineKeyboardMarkup:
    """
    Admin uchun tasdiqlash/rad etish tugmalari.
    callback_data format: "admin:<action>:<type>:<id>"
    Misol: "admin:approve:topup:12" yoki "admin:decline:order:5"
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash / Approve",
                    callback_data=f"admin:approve:{type_}:{pid}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish / Reject",
                    callback_data=f"admin:decline:{type_}:{pid}"
                ),
            ]
        ]
    )
# ===================== PRODUCT CRUD (ADMIN) =====================

def product_crud_kb(pid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"product:edit:{pid}"),
            InlineKeyboardButton(text="🗑 O‘chirish", callback_data=f"product:delete:{pid}")
        ]
    ])


def add_product_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Mahsulot qo‘shish", callback_data="product:add")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:menu")]
    ])


# ===================== USERS =====================

def user_balance_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Balansni o‘zgartirish", callback_data=f"user:balance:{uid}")],
    ])