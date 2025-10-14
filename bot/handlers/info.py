from aiogram import Router, types

router = Router()

@router.message(lambda m: m.text == "ℹ️ Ma’lumot")
async def info_section(message: types.Message):
    await message.answer(
        "📘 Bu bot orqali siz to‘lovlarni amalga oshirishingiz mumkin.\n"
        "Barcha ma’lumotlar xavfsiz saqlanadi 🔒"
    )
