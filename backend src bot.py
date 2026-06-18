"""
File-level: Entry point for Mikky aiogram bot.
Initializes bot, DB pool, registers handlers and starts polling.
"""

import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from .handlers import router
from .db import init_db_pool, close_db_pool
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is required in environment")

async def main():
    """
    Initialize DB pool, bot, register routers and start polling.
    """
    await init_db_pool()
    storage = MemoryStorage()
    session = AiohttpSession()
    bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode="HTML", session=session)
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    try:
        print("Starting Mikky bot (polling)...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_db_pool()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
