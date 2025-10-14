from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

router = Router()

def main_reply_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Coin"), KeyboardButton("🏆 Rank"))
    kb.add(KeyboardButton("💳 Hisobni to'ldirish"), KeyboardButton("📦 Buyurtmalarim"))
    kb.add(KeyboardButton("⚙ Til / Settings"))
    return kb

# /start yoki boshqa joydan asosiy menyu olish uchun
@router.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Xush kelibsiz! Asosiy menyu:", reply_markup=main_reply_kb())

# Agar foydalanuvchi asosiy menyudan Coin tugmasini bosadi (ReplyKeyboard tugma)
@router.message(lambda m: m.text == "💰 Coin")
async def coin_open(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Gold Coin", callback_data="coin:gold")],
        [InlineKeyboardButton(text="Silver Coin", callback_data="coin:silver")],
        [InlineKeyboardButton(text="⬅ Orqaga", callback_data="back:main")]
    ])
    # reply_markup Inline — yangi xabarda ko'rsatamiz (reply keyboardni saqlash uchun `reply_markup` ni o'zgartirmaymiz)
    await message.answer("Coin turini tanlang:", reply_markup=kb)

# Agar foydalanuvchi Rank tugmasini bosadi
@router.message(lambda m: m.text == "🏆 Rank")
async def rank_open(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Bronze", callback_data="rank:bronze")],
        [InlineKeyboardButton(text="Silver", callback_data="rank:silver")],
        [InlineKeyboardButton(text="⬅ Orqaga", callback_data="back:main")]
    ])
    await message.answer("Rank turini tanlang:", reply_markup=kb)

# Callback query handlerlar
@router.callback_query(lambda c: c.data and c.data.startswith("coin:"))
async def handle_coin_callback(callback: types.CallbackQuery):
    await callback.answer()  # to'siqni olib tashlash (notification)
    _, coin_type = callback.data.split(":", 1)
    # bu yerda coin_type bo'yicha ish yuritish mumkin
    await callback.message.answer(f"Siz tanladingiz: Coin — {coin_type.capitalize()}")

@router.callback_query(lambda c: c.data and c.data.startswith("rank:"))
async def handle_rank_callback(callback: types.CallbackQuery):
    await callback.answer()
    _, rank_type = callback.data.split(":", 1)
    await callback.message.answer(f"Siz tanladingiz: Rank — {rank_type.capitalize()}")

# Orqaga tugmasi: asosiy menyuni qaytarish
@router.callback_query(lambda c: c.data == "back:main")
async def handle_back_main(callback: types.CallbackQuery):
    await callback.answer()
    # edit qilmaysiz, balki yangi xabarga asosiy reply keyboardni yuborasiz
    await callback.message.answer("Asosiy menyu:", reply_markup=main_reply_kb())
