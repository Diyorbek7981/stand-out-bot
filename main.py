from config import bot, ADMIN
from aiogram import Bot, Dispatcher
import asyncio
import logging
from handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()


async def bot_stopped():
    await bot.send_message(ADMIN, '🛑Bot to\'xtadi!!!')


async def bot_started():
    await bot.send_message(ADMIN, "🏁Bot ishga tushdi!!!")


async def start():
    dp.startup.register(bot_started)
    dp.shutdown.register(bot_stopped)
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start())
