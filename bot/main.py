import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from db import init_db
from handlers import router  # router barcha child-routerni o'z ichiga oladi

logging.basicConfig(level=logging.INFO)

async def main():
    init_db()
    logging.info("✅ Database tayyor.")

    bot = Bot(token="8317966549:AAEIb0v6tnLMjkb5wc7Iw-XscOJg8mj9wEM", default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)

    print("🤖 Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
