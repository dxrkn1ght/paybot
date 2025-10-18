from aiogram import Router, types, F
from aiogram.types import Message
from keyboards import main_menu, products_type_kb
from db import get_or_create_user, set_user_lang
from config import DEFAULT_LANG

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    user = get_or_create_user(message.from_user.id)
    # language selection inline (simple)
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
           types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"))
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=kb)

@router.callback_query(F.data.startswith("lang_"))
async def lang_set(call: types.CallbackQuery):
    lang = call.data.split("lang_")[1]
    set_user_lang(call.from_user.id, lang)
    kb = main_menu(lang)
    if lang == "ru":
        txt = "Привет! Добро пожаловать в SunLite. Используйте меню."
    else:
        txt = "Salom! SunLite botga xush kelibsiz. /products va /topup dan foydalaning."
    await call.message.answer(txt, reply_markup=kb)
    await call.answer()
