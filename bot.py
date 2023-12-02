import asyncio, time
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook

from aiogram.fsm.storage.redis import RedisStorage, Redis

from config_data.config import load_config
from handlers import admin_handlers, user_handlers
from lexicon.lexicon_ru import USER_MENU, ADMIN_MENU
from models.methods import create_db_and_tables
from scheduling.scheduling import scheduler

async def on_startup():
    scheduler.start()


create_db_and_tables()

config = load_config()
BOT_TOKEN = config.tg_bot.token

bot = Bot(BOT_TOKEN)


redis = Redis(host='redis', port=6379)
storage = RedisStorage(redis=redis)


dp = Dispatcher(storage=storage)

dp.include_routers(user_handlers.router, admin_handlers.router)
dp.startup.register(on_startup)

async def main():
    print('-' * 10 + 'START' + '-' * 10)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f'{10 * "-"} KeyboardInterrupt {10 * "-"}')
        exit()