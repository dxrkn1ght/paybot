from aiogram import Router, types
from aiogram.filters import Command
from keyboards import main_menu
from config import OWNER_CHAT_ID

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Salom! SunLite botga xush kelibsiz.\nQuyidagi menyudan tanlang:", reply_markup=main_menu)
