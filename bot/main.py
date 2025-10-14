import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from config import BOT_TOKEN
from handlers import router as handlers_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(
        token='8317966549:AAEIb0v6tnLMjkb5wc7Iw-XscOJg8mj9wEM',
        default=DefaultBotProperties(parse_mode="HTML")  # Aiogram 3.7+ usuli
    )
    dp = Dispatcher()
    dp.include_router(handlers_router)
    logger.info("🚀 SunLite Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
