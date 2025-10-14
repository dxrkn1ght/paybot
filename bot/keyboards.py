from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎒 Mahsulotlar")],
        [KeyboardButton(text="💳 Hisobni to'ldirish")],
        [KeyboardButton(text="📦 Buyurtmalarim")],
        [KeyboardButton(text="⚙️ Til / Settings")],
    ],
    resize_keyboard=True
)


# After selecting product type (coin or rank)
product_types_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💎 Coin", callback_data="type_coin"),
         InlineKeyboardButton(text="⭐ Rank", callback_data="type_rank")],
    ]
)

def products_inline(products):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for p in products:
        kb.inline_keyboard.append([InlineKeyboardButton(text=f"{p['name']} — {p['price']} so'm", callback_data=f"buy_{p['code']}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_menu")])
    return kb
