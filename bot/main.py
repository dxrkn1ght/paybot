import asyncio, logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import router as handlers_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(handlers_router)
    logger.info("🚀 SunLite Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
