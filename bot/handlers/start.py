from aiogram import Router, types
from aiogram.filters import CommandStart

dp = Router()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("👋 Salom! Bot muvaffaqiyatli ishga tushdi ✅")
