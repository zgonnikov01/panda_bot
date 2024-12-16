import json

from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter, CommandStart, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
import datetime

from config_data.config import load_config
from lexicon.lexicon_ru import LEXICON
from models.models import Game, Promo, Giveaway
from models.methods import save_game, get_users, get_game, save_promo, get_promo,\
    get_promos, toggle_promo, delete_promo, update_user, get_game_results, \
    get_user_by_username, get_giveaway, update_game, get_giveaways, update_all_users
from states.states import FSMLotteryUpload
from handlers.utils import get_current_date, get_mongodb


config = load_config()
router = Router()


def send_animation(path: str):
    #if not in tg cache, add to cache
    #else send from tg cache
    

@router.message(Command(commands='spin'), StateFilter(default_state))
async def spin(message: Message, bot: Bot, state: FSMContext):
    mongodb = get_mongodb()
    lottery_state = mongodb.lottery_state.find_one()
    if not lottery_state:
        await message.answer('Сегодня Панда Бо не проводит лотерею')
        return
    lottery = mongodb.lotteries.find_one({'label': lottery_state[label]})
    user = get_user(user_id=message.from_user.id)
    if user.user_id in lottery['spin_history'] and \
            [datetime.datetime.now().date()] in lottery['spin_history'][user.user_id]:

        await message.answer(
            text='Играть в лотерею можно только один раз в день, попробуй завтра'
        )
        return
    
    # check if user hasn't won more than 2 times in last 7 days
    
    option = random.choice(lottery_state['bonus_points']['options'])

    if lottery_state['gifts'] and random() * 100 < lottery['gift_percent']:
        gift = random.choices(
            population=lottery_state['gifts'].keys(),
            weights=lottery_state['gifts'].values(),
        )[0]

        lottery['gifts'][gift] -= 1
        if lottery['gifts'][gift] == 0:
            lottery['gifts'].pop(gift)

        lottery_state['gifts'][gift] -= 1
        if lottery_state['gifts'][gift] == 0:
            lottery_state['gifts'].pop(gift)

        # SEND ANIMATION {gift}.mov
        # REPLY WITH INSTRUCTION

    elif random() * 100 < lottery['bonus_point_percent']:
        if option <= lottery_state['bonus_pounts']['quantity']:
            lottery_state['bonus_pounts']['quantity'] -= option
            # SEND ANIMATION bonus.mov
            # SOMEHOW GIVE POINTS TO USER
            # REPLY WITH INSTRUCTION
    else:
        # SEND ANIMATION nothing.mov

    mongodb.lottery_state.find_one_and_replace(
        replacement=lottery_state    
    )
    mongodb.lotteries.find_one_and_replace(
        filter={'label': lottery_state[label]}
        replacement=lottery
    )

