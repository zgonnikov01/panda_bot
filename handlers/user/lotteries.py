import json, random, datetime

from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter, CommandStart, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from config_data.config import load_config
from lexicon.lexicon_ru import LEXICON
from models.methods import get_user
from states.states import FSMLotteryUpload
from handlers.utils import get_current_date, get_mongodb


config = load_config()
router = Router()


async def answer_animation(message: Message, animation_path: str):
    mongodb = get_mongodb()
    animation = mongodb.assets.find_one({'animation_path': animation_path})
    print(animation_path, animation)
    if animation != None:
        await message.answer_animation(
            animation=animation['file_id'],
            duration=15,
            height=200,
            width=200
        )
    else:
        animation = FSInputFile(animation_path)
        msg = await message.answer_animation(
            animation=FSInputFile(animation_path),
            duration=15,
            height=200,
            width=200
        )
        mongodb.assets.insert_one({
            'animation_path': animation_path,
            'file_id': msg.document.file_id
        })


@router.message(Command(commands='spin'), StateFilter(default_state))
async def spin(message: Message, bot: Bot, state: FSMContext):
    mongodb = get_mongodb()
    lottery_state = mongodb.lottery_state.find_one()
    if not lottery_state:
        await message.answer('Сегодня Панда Бо не проводит лотерею')
        return
    lottery = mongodb.lotteries.find_one({'label': lottery_state['label']})
    user_id = str(message.from_user.id)
    if 'spin_history' in lottery and \
            user_id in lottery['spin_history'] and \
            datetime.datetime.now().date().isoformat() in lottery['spin_history'][user_id]:

        await message.answer(
            text='Играть в лотерею можно только один раз в день, попробуй завтра'
        )
        return
    
    # check if user hasn't won more than 2 times in last 7 days
    
    option = random.choice(lottery_state['bonus_points']['options'])

    if lottery_state['gifts'] and random.random() * 100 < lottery['gift_percent']:
            gift = random.choices(
                population=list(lottery_state['gifts'].keys()),
                weights=list(lottery_state['gifts'].values()),
            )[0]

            lottery['gifts'][gift] -= 1
            if lottery['gifts'][gift] == 0:
                lottery['gifts'].pop(gift)

            lottery_state['gifts'][gift] -= 1
            if lottery_state['gifts'][gift] == 0:
                lottery_state['gifts'].pop(gift)

            await answer_animation(
                message=message,
                animation_path=f'assets/lottery/{gift}.gif'
            )
            await message.answer(gift)
            result = gift
            
            # REPLY WITH INSTRUCTION

    elif random.random() * 100 < lottery['bonus_point_percent'] and \
            int(option) <= lottery_state['bonus_points']['quantity']:
        lottery_state['bonus_points']['quantity'] -= option
        await answer_animation(
            message=message,
            animation_path='assets/lottery/bonus_points.gif'
        )
        await message.answer(f'bonus{option}')
        result = f'bonus{option}'
        # SOMEHOW GIVE POINTS TO USER
        mongodb.bonus.insert_one({
            'tg_id': user_id,
            'amount': int(option),
            'datetime': datetime.datetime.now()
        })
        # REPLY WITH INSTRUCTION
    else:
        await answer_animation(
            message=message,
            animation_path='assets/lottery/nothing.gif'
        )
        await message.answer('nothing')
        result = 'nothing'
    
    if 'spin_history' not in lottery:
        lottery['spin_history'] = {}
    if user_id not in lottery['spin_history']:
        lottery['spin_history'][user_id] = {}
    lottery['spin_history'][user_id][datetime.datetime.now().date().isoformat()] = result
    mongodb.lottery_state.find_one_and_replace(
        filter={'label': lottery_state['label']},
        replacement=lottery_state    
    )
    mongodb.lotteries.find_one_and_replace(
        filter={'label': lottery_state['label']},
        replacement=lottery
    )

