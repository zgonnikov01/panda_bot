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
from models.methods import get_user
from bamps import bamps
from handlers.utils import get_current_date, get_mongodb, wrap_as_json_code


config = load_config()
router = Router()
router.message.filter(lambda message: message.from_user.id in config.tg_bot.admin_ids)

 
@router.message(Command(commands='balance'), StateFilter(default_state))
async def get_balance(message: Message, bot: Bot, state: FSMContext):
    user = get_user(message.from_user.id)
    if user == None or user.phone == None:
        await message.answer('Для работы с бонусной программой сначала нужно зарегистрироваться. Используй команду /register')
        return
    try:
        balance = bamps.get_balance(user.phone)
        await message.answer(f'На твоём счету {balance} бонусных баллов')
    except Exception as e:
        await message.answer('Не получилось проверить баланс. Помни, для того, чтобы работать с бонусной программой, тебе нужно зарегистрироваться в ней. Для этого скачай приложение по ссылке https://join2.club/panda')


@router.message(Command(commands='check_refill'), StateFilter(default_state))
async def check_refill(message: Message, bot: Bot, state: FSMContext):
    mongodb = get_mongodb()
    bonus_list = list(
        mongodb.bonus\
            .aggregate([
                {
                    '$match': {
                        'datetime': {
                            '$gte':
                                datetime.datetime.now() - datetime.timedelta(days=7)
                        }
                    },
                },
                {
                    '$group': {
                        '_id': '$tg_id',
                        'quantity': {
                            '$sum': '$amount'
                        }
                    }
                }
            ])
    )
    await message.answer(f'Current bonus points to refill: {wrap_as_json_code(bonus_list)}', parse_mode='HTML')


@router.message(Command(commands='refill'), StateFilter(default_state))
async def refill(message: Message, bot: Bot, state: FSMContext):
    mongodb = get_mongodb()
    bonus_list = list(
        mongodb.bonus\
            .aggregate([
                {
                    '$match': {
                        'datetime': {
                            '$gte':
                                datetime.datetime.now() - datetime.timedelta(days=7)
                        }
                    },
                },
                {
                    '$group': {
                        '_id': '$tg_id',
                        'quantity': {
                            '$sum': '$amount'
                        }
                    }
                }
            ])
    )
    await message.answer(f'Current bonus points to refill: {wrap_as_json_code(bonus_list)}', parse_mode='HTML')
      
