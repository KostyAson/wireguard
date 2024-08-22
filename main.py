import asyncio
import aiogram
import handlers.info
import handlers.pay
import handlers.management
import dotenv
import os

dotenv.load_dotenv('.env')

bot = aiogram.Bot(token=os.getenv('bot'))

dp = aiogram.Dispatcher()

dp.include_router(handlers.info.router)
dp.include_router(handlers.pay.router)
dp.include_router(handlers.management.router)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
