from aiogram import Router, types, F
from aiogram.types import Message
from keyboards import main_menu
from db import get_or_create_user, set_user_lang
from config import DEFAULT_LANG

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    user = get_or_create_user(message.from_user.id)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
            types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        ]
    ])
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=kb)


@router.callback_query(F.data.startswith("lang_"))
async def lang_set(call: types.CallbackQuery):
    lang = call.data.split("lang_")[1]
    set_user_lang(call.from_user.id, lang)
    kb = main_menu(lang)
    txt = (
        "Salom! SunLite botga xush kelibsiz. /products va /topup dan foydalaning."
        if lang == "uz"
        else "Привет! Добро пожаловать в SunLite. Используйте меню."
    )
    await call.message.answer(txt, reply_markup=kb)
    await call.answer()
