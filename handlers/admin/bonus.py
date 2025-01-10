import json

from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter, CommandStart, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
import datetime

from config_data.config import load_config
from lexicon.lexicon_ru import LEXICON, Lexicon
from models.methods import get_user
from bamps import bamps
from handlers.utils import get_current_date, get_mongodb, wrap_as_json_code, format_number


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
        balance = await bamps.get_balance(user.phone)
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
                            '$gte': datetime.datetime.now() - datetime.timedelta(days=777),
                            '$lte': datetime.datetime.now()
                        }
                    },
                },
                {
                    '$group': {
                        '_id': '$tg_id',
                        'quantity': {
                            '$sum': '$amount'
                        }
                    },
                    'phone': {
                        '$first': '$phone'
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
                            '$gte': datetime.datetime.now() - datetime.timedelta(days=777),
                            '$lte': datetime.datetime.now()
                        }
                    },
                },
                {
                    '$group': {
                        '_id': '$tg_id',
                        'quantity': {
                            '$sum': '$amount'
                        },
                        'phone': {
                            '$first': '$phone'
                        }
                    }
                }
            ])
        )


    for bonus in bonus_list:
        user = get_user(bonus['_id'])
        bonus['phone'] = format_number(user.phone)
    
    await message.answer(f'Current bonus points to refill: {wrap_as_json_code(bonus_list)}', parse_mode='HTML')

    refilled = []
    result_success = []
    result_no_account = []
    result_error = []

    for bonus in bonus_list:
        try:
            balance = await bamps.get_balance(bonus['phone'])
            if balance:
                #await bamps.refill(phone_number=bonus['phone'], amount=str(bonus['quantity']))
                result_success.append(f'🟢 Success {bonus["_id"], bonus["phone"], await bamps.get_balance(bonus["phone"])}')
                mongodb.bonus.find_one_and_replace(
                    filter={'tg_id': bonus['_id']},
                    replacement={
                        'tg_id': bonus['_id'],
                        'amount': -bonus['quantity'],
                        'datetime': datetime.datetime.now() + datetime.timedelta(days=7)
                    }
                )
                #await bot.send_message(
                #    chat_id=bonus['_id'],
                #    text=Lexicon.User.refill_success
                #) 
            else:
                #await bot.send_message(
                #    chat_id=bonus['_id'],
                #    text=Lexicon.User.refill_no_account
                #) 
                result_no_account.append(f'🟡 No account: {bonus["_id"], bonus["phone"]}')
        except Exception as e:
            result_error.append(f'🔴 Error: {bonus["_id"], bonus["phone"]}')

    result = '\n'.join([
        f'Success ({len(result_success)}):',
        '\n\t'.join(result_success),
        f'No account ({len(result_no_account)}):',
        '\n\t'.join(result_no_account),
        f'Error ({len(result_error)}):',
        '\n\t'.join(result_error)
    ])

    wrapped_result = f'<pre><code class="language-json">{result}</code></pre>'

    await message.answer(f'Operation finished: {wrapped_result}', parse_mode='HTML')

