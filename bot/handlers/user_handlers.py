from aiogram import Router, types
from bot.keyboards.main_menu import main_menu
from bot.database import get_products_by_type

router = Router()

@router.message(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("👋 Salom! SunLite botga xush kelibsiz.\nQuyidagi menyudan tanlang:", reply_markup=main_menu())

@router.callback_query(lambda c: c.data.startswith("show_"))
async def show_products(callback: types.CallbackQuery):
    type_ = callback.data.split("_")[1]
    products = get_products_by_type(type_)
    if not products:
        await callback.message.edit_text(f"❌ {type_.capitalize()}lar topilmadi.")
        return
    text = f"📦 {type_.capitalize()}lar ro‘yxati:\n\n"
    for name, price in products:
        text += f"• {name} — {price} so‘m\n"
    await callback.message.edit_text(text, reply_markup=main_menu())
