import asyncio, logging
from aiogram import Bot
import config
from handlers import dp as dispatcher
logging.basicConfig(level=logging.INFO)
async def main():
    if not config.BOT_TOKEN:
        print('Error: BOT_TOKEN not set in .env')
        return
    bot = Bot(token=config.BOT_TOKEN)
    try:
        print('🚀 SunLite Bot starting...')
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
if __name__ == '__main__':
    asyncio.run(main())
