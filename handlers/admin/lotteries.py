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
router.message.filter(lambda message: message.from_user.id in config.tg_bot.admin_ids)

 
@router.message(Command(commands='lottery_upload_config'), StateFilter(default_state))
async def upload_lottery_config(message: Message, bot: Bot, state: FSMContext):
    # reply "Send me your shit"
    # also send blank config
    await message.answer('Send me your shit')
    await state.set_state(FSMLotteryUpload.get_json)


@router.message(StateFilter(FSMLotteryUpload.get_json))
async def upload_lottery_config_save(message: Message, bot: Bot, state: FSMContext):
    # would be nice to check if time intervals overlap, but I'm tight on time right now
    try:
        lottery_dict = json.loads(message.text)
        lottery_dict['start'] = datetime.datetime.fromisoformat(lottery_dict['start'])
        lottery_dict['end'] = datetime.datetime.fromisoformat(lottery_dict['end'])
    except Exception as e:
        await message.answer('Incorrect json')
        await state.clear()
        return
    try:
        mongodb = get_mongodb()
        mongodb.lotteries.insert_one(lottery_dict)
    except Exception as e:
        await message.answer(f'Exception:\n\n{e}')
        await state.clear()
        return
    await message.answer('OK')
    await state.clear()


@router.message(Command(commands='lottery_get_info'), StateFilter(default_state))
async def get_lottery_info(message: Message, bot: Bot, state: FSMContext):
    # reply with current_prize_pool in json format
    await message.answer('Not implemented yet')
