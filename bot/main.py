import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import router as handlers_router


# --- Bot commandlar ro'yxati (bot menyusi uchun)
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushurish"),
        BotCommand(command="help", description="Yordam olish"),
    ]
    await bot.set_my_commands(commands)


# --- Asosiy ishga tushirish funksiyasi
async def main():
    bot = Bot(token="8317966549:AAEIb0v6tnLMjkb5wc7Iw-XscOJg8mj9wEM", parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    # routerlarni ulaymiz
    dp.include_router(handlers_router)

    # Bot commandlarini o‘rnatamiz
    await set_commands(bot)

    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("❌ Bot to‘xtatildi.")
