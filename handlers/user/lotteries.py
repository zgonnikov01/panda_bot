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

quotes = [
    'Сегодня — отличный день для новых начинаний!',
    'Ты способен на большее, чем думаешь.',
    'Каждый шаг вперед — это шаг к успеху.',
    'Не бойся мечтать: твои мечты могут стать реальностью!',
    'С каждым днем ты становишься лучше.',
    'Счастье — это выбор. Выбирай его сегодня!',
    'Улыбка — это солнечный свет для окружающих.',
    'Верь в себя, и весь мир поверит в тебя!',
    'Ошибки — это часть пути к успеху. Учись на них!',
    'Каждый день — это новая возможность стать счастливее.',
    'Ты — источник вдохновения для других.',
    'Не забывай радоваться мелочам. Они делают жизнь прекрасной!',
    'Ты уникален, и в этом твоя сила.',
    'Делай то, что любишь, и успех последует за тобой.',
    'Позитивные мысли притягивают позитивные события.',
    'Просто будь собой — это достаточно для счастья.',
    'Ищи хорошее в каждом дне: оно обязательно найдется!',
    'Ты заслуживаешь всего самого лучшего.',
    'Все, что ты делаешь с любовью, становится прекрасным.',
    'Вкладывай свою энергию в то, что приносит удовольствие.',
    'Ты — магнит для хороших людей и событий.',
    'Жизнь полна чудес, только нужно уметь их замечать!',
    'Пусть каждый момент будет наполнен радостью.',
    'Смотри на мир с надеждой и оптимизмом.',
    'Ты уже сделал много, не останавливайся на достигнутом!',
    'Ты — творец своей судьбы. Создавай её с любовью!',
    'Открывай новое и познавай мир вокруг.',
    'Заботься о себе — это первый шаг к счастью.',
    'Делай добрые дела, и они вернутся к тебе.',
    'Настроение создается с утра — начни его с улыбки!',
    'Будь смелым, делая шаги к своим мечтам.',
    'Ты способен преодолеть любые трудности.',
    'Жизнь — это путешествие, наслаждайся каждым моментом.',
    'Верность своим желаниям приведет к успеху.',
    'Открывай свое сердце для любви и дружбы.',
    'Пусть сегодня принесет тебе положительные эмоции!',
    'Твоя энергия — это твоя сила.',
    'Постигай новые горизонты и стремись к высотам!',
    'Настрой себя на успех, и он найдет тебя.',
    'Ты создаешь свою реальность — делай её светлой!',
    'Делай выбор в пользу счастья каждый день.',
    'Живи в гармонии с собой и окружающим миром.',
    'Каждый новый день — это новая страница твоей истории.',
    'Слушай свое сердце и следуй его голосу.',
    'Радуйся своему пути и тому, что ты достиг!',
    'Доброта возвращается, передавай её дальше.',
    'Не сравнивай себя с другими, ты уникален!',
    'Забота о других — это ключ к собственному счастью.',
    'Каждый момент важен — наполняй его смыслом.',
    'Начни этот день с позитивного намерения и смотри, как он изменится!'
]


@router.message(Command(commands='spin'), StateFilter(default_state))
async def spin(message: Message, bot: Bot, state: FSMContext):
    mongodb = get_mongodb()
    lottery_state = mongodb.lottery_state.find_one()
    if not lottery_state:
        await message.answer('Столько дел навалилось на Панду Бо🐼\n\nК сожалению, он сейчас не может поиграть с тобой😔\n\nНо завтра может все поменяться🤩')
        return
    lottery = mongodb.lotteries.find_one({'label': lottery_state['label']})
    user_id = str(message.from_user.id)
    if 'spin_history' in lottery and \
            user_id in lottery['spin_history'] and \
            datetime.datetime.now().date().isoformat() in lottery['spin_history'][user_id]:

        await message.answer(
            text='Кажется, сегодня ты уже играл🐼\n\nПриходи завтра - уверен, что ты победишь☝🏻'
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
            result = gift
            if gift == 'pizza':
                await message.answer('Поздравляю🐼✨\n\nТы только что выиграл фантастическую пиццу Пепперони от Панды Бо🥳\n\nВот это удача 🍀 \n\nЧтобы забрать приз, позвони нашим волшебным помощникам на горячую линию 8-800-600-65-63 и сообщи, что ты выиграл')
            elif gift == 'mochi':
                await message.answer('Поздравляю🐼✨\n\nТы только что выиграл вкуснейший ролл Филадельфия от Панды Бо🥳\n\nВот это удача 🍀 \n\nЧтобы забрать приз, позвони нашим волшебным помощникам на горячую линию 8-800-600-65-63 и сообщи, что ты выиграл')
            elif gift == 'rolls':
                await message.answer('Поздравляю🐼✨\n\nТы только что выиграл вкуснейший ролл Филадельфия от Панды Бо🥳\n\nВот это удача 🍀 \n\nЧтобы забрать приз, позвони нашим волшебным помощникам на горячую линию 8-800-600-65-63 и сообщи, что ты выиграл')


    elif random.random() * 100 < lottery['bonus_point_percent'] and \
            int(option) <= lottery_state['bonus_points']['quantity']:
        lottery_state['bonus_points']['quantity'] -= option
        lottery['bonus_points']['quantity'] -= option
        await answer_animation(
            message=message,
            animation_path='assets/lottery/bonus_points.gif'
        )
        result = f'bonus{option}'
        # SOMEHOW GIVE POINTS TO USER
        mongodb.bonus.insert_one({
            'tg_id': user_id,
            'amount': int(option),
            'datetime': datetime.datetime.now()
        })
        # REPLY WITH INSTRUCTION
        await message.answer(quotes[random.randint(0, 49)])
        await message.answer(f'Поздравляю🐼✨\n\nТы только что выиграл {option} бонусных баллов от Панды Бо🥳\n\nВот это удача 🍀 \n\nБаллы начислятся тебе на счёт в течение 3-х рабочих дней, только не забудь зарегистрироваться в бонусной программе: https://join2.club/panda')
    else:
        await answer_animation(
            message=message,
            animation_path='assets/lottery/nothing.gif'
        )
        #await message.answer('Сегодня удача прошла мимо тебя, но расстраивайся 🐼☝\n\nЗавтра ты можешь попробовать еще раз🤩')
        await message.answer(quotes[random.randint(0, 49)])
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

