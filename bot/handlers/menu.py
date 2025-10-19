from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from db import get_balance  # balansni olish uchun db.py dan import

router = Router()


# =====================================================
# ✅ Asosiy menyu ReplyKeyboard
# =====================================================
def main_reply_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Coin"), KeyboardButton("🏆 Rank"))
    kb.add(KeyboardButton("💳 Hisobni to'ldirish"), KeyboardButton("📦 Buyurtmalarim"))
    kb.add(KeyboardButton("💰 Mening balansim"))  # Balans tugmasi
    kb.add(KeyboardButton("⚙ Til / Settings"))
    return kb


# =====================================================
# /start yoki boshqa joydan asosiy menyu olish
# =====================================================
@router.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Xush kelibsiz! Asosiy menyu:", reply_markup=main_reply_kb())


# =====================================================
# 💰 Coin tugmasi
# =====================================================
@router.message(lambda m: m.text == "💰 Coin")
async def coin_open(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Gold Coin", callback_data="coin:gold")],
        [InlineKeyboardButton(text="Silver Coin", callback_data="coin:silver")],
        [InlineKeyboardButton(text="⬅ Orqaga", callback_data="back:main")]
    ])
    await message.answer("Coin turini tanlang:", reply_markup=kb)


# =====================================================
# 🏆 Rank tugmasi
# =====================================================
@router.message(lambda m: m.text == "🏆 Rank")
async def rank_open(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Bronze", callback_data="rank:bronze")],
        [InlineKeyboardButton(text="Silver", callback_data="rank:silver")],
        [InlineKeyboardButton(text="⬅ Orqaga", callback_data="back:main")]
    ])
    await message.answer("Rank turini tanlang:", reply_markup=kb)


# =====================================================
# 💰 Balansni ko‘rsatish
# =====================================================
@router.message(lambda m: m.text == "💰 Mening balansim")
async def my_balance(message: types.Message):
    balance = get_balance(message.from_user.id)
    await message.answer(f"💰 Sizning balansingiz: {balance:,} so‘m")


# =====================================================
# Callback query: Coin
# =====================================================
@router.callback_query(lambda c: c.data and c.data.startswith("coin:"))
async def handle_coin_callback(callback: types.CallbackQuery):
    await callback.answer()  # notificationni o‘chirish
    _, coin_type = callback.data.split(":", 1)
    await callback.message.answer(f"Siz tanladingiz: Coin — {coin_type.capitalize()}")


# =====================================================
# Callback query: Rank
# =====================================================
@router.callback_query(lambda c: c.data and c.data.startswith("rank:"))
async def handle_rank_callback(callback: types.CallbackQuery):
    await callback.answer()
    _, rank_type = callback.data.split(":", 1)
    await callback.message.answer(f"Siz tanladingiz: Rank — {rank_type.capitalize()}")


# =====================================================
# Callback query: Orqaga (Asosiy menyu)
# =====================================================
@router.callback_query(lambda c: c.data == "back:main")
async def handle_back_main(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Asosiy menyu:", reply_markup=main_reply_kb())
