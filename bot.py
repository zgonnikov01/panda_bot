import asyncio, time
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.types import BotCommand



from aiogram.fsm.storage.redis import RedisStorage, Redis

import handlers.admin.lotteries
import handlers.admin.bonus
import handlers.user.lotteries
import handlers.user.registration
from handlers import admin_handlers, user_handlers
from config_data.config import config
from lexicon.lexicon_ru import USER_MENU, ADMIN_MENU
from models.methods import create_db_and_tables
from scheduling.scheduling import scheduler
from scheduling import jobs



async def on_startup():
    scheduler.start()
    job = scheduler.add_job(jobs.lotteries.update_state, 'cron', hour=0)
    print(job)
    items = [BotCommand(command=item[0], description=item[1]) for item in USER_MENU.items()]
    await bot.set_my_commands(commands=items)

    #print('trying to clear state for user 720747122...')
    #state = await Dispatcher.get_current().current_state(user=720747122)
    #await state.clear()
    #print('state cleared')

    #await update_lotteries()


create_db_and_tables()

BOT_TOKEN = config.tg_bot.token

bot = Bot(BOT_TOKEN)


redis = Redis(host='redis', port=6379)
storage = RedisStorage(redis=redis)


dp = Dispatcher(storage=storage)

dp.include_routers(
    admin_handlers.router,
    handlers.admin.bonus.router,
    handlers.admin.lotteries.router,
    handlers.user.registration.router,
    handlers.user.lotteries.router,
    user_handlers.router,
)
dp.startup.register(on_startup)

async def main():
    print('-' * 10 + 'START' + '-' * 10)
    await bot(DeleteWebhook(drop_pending_updates=True))
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f'{10 * "-"} KeyboardInterrupt {10 * "-"}')
        exit()

