import asyncio, time, datetime
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook

from aiogram.fsm.storage.redis import RedisStorage, Redis

import handlers.admin.lotteries
import handlers.admin.bonus
import handlers.user.lotteries
from handlers import admin_handlers, user_handlers
from config_data.config import load_config
from lexicon.lexicon_ru import USER_MENU, ADMIN_MENU
from models.methods import create_db_and_tables
from scheduling.scheduling import scheduler
from handlers.utils import get_current_date, get_mongodb


async def on_startup():
    scheduler.start()
    job = scheduler.add_job(update_lotteries, 'cron', hour=0)
    print(job)
    #await update_lotteries()


async def update_lotteries():
    mongodb = get_mongodb()
    try:
        current_lottery = mongodb.lotteries.find_one({
            'start': {'$lte': datetime.datetime.now()},
            'end': {'$gt': datetime.datetime.now()}
        })
    except Exception as e:
        print(e)
    try:
        mongodb.lottery_state.drop()
    except Exception as e:
        print(e)
    try:
        if current_lottery:
            n = (current_lottery['end'] - datetime.datetime.now()).days
            gifts = {
                key: value // n for key, value in current_lottery['gifts'].items()
            }
            bonus_points = {
                'quantity': current_lottery['bonus_points']['quantity'] // n,
                'options': current_lottery['bonus_points']['options']
            }
            mongodb.lottery_state.insert_one({
                'label': current_lottery['label'],
                'gifts': gifts,
                'bonus_points': bonus_points
            })
    except Exception as e:
        print(e)


create_db_and_tables()

config = load_config()
BOT_TOKEN = config.tg_bot.token

bot = Bot(BOT_TOKEN)


redis = Redis(host='redis', port=6379)
storage = RedisStorage(redis=redis)


dp = Dispatcher(storage=storage)

dp.include_routers(
    admin_handlers.router,
    handlers.admin.bonus.router
    handlers.admin.lotteries.router,
    handlers.user.lotteries.router,
    user_handlers.router,
)
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

