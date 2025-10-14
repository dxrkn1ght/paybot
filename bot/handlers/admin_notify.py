# handlers/admin_notify.py
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command(commands=["notify"]))
async def notify_admin(message: types.Message):
    await message.answer("Adminga xabar yuborildi (demo).")
