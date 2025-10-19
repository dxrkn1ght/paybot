import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage  # FSM uchun
from config import BOT_TOKEN
from handlers import router as main_router  # barcha handlerlarni ichiga olgan init.py
from db import init_db  # <<< bazani init qilish uchun

logging.basicConfig(level=logging.INFO)

async def main():
    # bazani init qilamiz
    init_db()

    bot = Bot(
        token="8317966549:AAEIb0v6tnLMjkb5wc7Iw-XscOJg8mj9wEM",
        default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(main_router)  # barcha routerlar shu yerda ulangan

    print("🤖 Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
