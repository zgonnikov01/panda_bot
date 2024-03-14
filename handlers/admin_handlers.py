import json

from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.chat import Chat
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from datetime import datetime, timedelta

from config_data.config import load_config
from lexicon.lexicon_ru import LEXICON
from models.models import Game, Promo, Giveaway
from models.methods import save_game, get_users, get_game, save_promo, get_promo,\
    get_promos, toggle_promo, delete_promo, update_user, get_game_results, \
    get_user_by_username, get_giveaway, update_game
from states.states import FSMCreateGame, FSMScheduleGame, FSMEchoPost, FSMStopGame,\
    FSMSavePromo, FSMEditPromos, FSMMessageUsers, FSMMessageUser, FSMGetGameResults, \
    FSMScheduleGiveaway, FSMLoadJsonGame
from keyboards.set_menu import set_admin_menu
from keyboards.keyboard_utils import create_inline_kb
from scheduling.scheduling import scheduler


class GameCallback(CallbackData, prefix='game'):
    type: str
    sequence_label: str

class GiveawayCallback(CallbackData, prefix='giveaway'):
    label: str

    
config = load_config()
router = Router()
router.message.filter(lambda message: message.from_user.id in config.tg_bot.admin_ids)


@router.message(CommandStart(), lambda message: message.from_user.id in config.tg_bot.admin_ids)
async def process_start_command(message: Message, bot: Bot, state: FSMContext):
    await set_admin_menu(message.from_user.id, bot)
    await message.answer(LEXICON['admin_start'])
    print(await state.get_state())


# @router.message(Command(commands='user_start'), lambda message: message.from_user.id in config.tg_bot.admin_ids)
# async def process_start_command(message: Message, bot: Bot, state: FSMContext):
#     await set_admin_menu(bot)
#     await message.answer(LEXICON['user_start'])
#     print(await state.get_state())


@router.message(Command(commands='cancel'))
async def process_cancel_create_game_command(message: Message, state: FSMContext):
    await message.answer('Отмена')
    await state.clear()
    print(await state.get_state())


@router.message(Command(commands='load_json_game'), StateFilter(default_state))
async def process_load_json_game_command(message: Message, state: FSMContext):
    await message.answer('Введите уникальный идентификатор последовательности')
    await state.set_state(FSMLoadJsonGame.set_sequence_label)
    print(await state.get_state())


@router.message(StateFilter(FSMLoadJsonGame.set_sequence_label))
async def process_load_json_game_command_set_label(message: Message, state: FSMContext):
    await state.update_data(sequence_label=message.text)
    await message.answer('Отправьте JSON')
    print(await state.get_state())


@router.message(StateFilter(FSMLoadJsonGame.load_json))
async def process_load_json_game_command_load_json(message: Message, state: FSMContext):
    json_string = message.text

    questions = json.loads(json_string)['вопросы']
    for index, question in enumerate(questions):
        question_text = question['вопрос']
        options = list(question['варианты ответов'].values())
        answer = question['варианты ответов'][question['правильный ответ']]
        full_answer = question['пояснение']
        print(options, answer, full_answer)
        sequence_label = (await state.get_data())['sequence_label']
        game = Game(
            text=question_text,
            sequence_label=sequence_label,
            label=f'{sequence_label}-{index + 1}',
            type='select',
            options='|'.join(options),
            answers=answer,
            images='',
            full_answer=full_answer,
            final_message=''
        )
        save_game(game)
        print(game)
    await message.answer(
            text='Отлично! Теперь нужно загрузить картинки для игры, когда все картинки будут загружены, нажмите на кнопку',
            reply_markup=create_inline_kb(1, {'Готово': 'images_uploaded'})
    )
    await state.set_state(FSMLoadJsonGame.request_pictures)
    print(await state.get_state())


@router.message(StateFilter(FSMLoadJsonGame.load_pictures), F.photo)
async def process_load_json_game_command_load_pictures(message: Message, state: FSMContext):
    try:
        images = (await state.get_data())['images']
    except:
        images = ''
    if images == '':
        await state.update_data(images=message.photo[-1].file_id)
    else:
        await state.update_data(images=images + '|' + message.photo[-1].file_id)
    print(await state.get_state())



@router.callback_query(StateFilter(FSMLoadJsonGame.save))
async def process_load_json_game_command_save(callback: CallbackQuery, state: FSMContext):
    print(await state.get_data())
    sequence_label = (await state.get_data())['sequence_label']
    images = (await state.get_data())['images'].split('|')
    for image in images:
        update_game(sequence_label=sequence_label, updates={'image': image})
    await state.clear()
    print(await state.get_state())
    await callback.message.delete()
    await callback.message.answer(text='Поздравляю, игра создана!')


@router.message(Command(commands='create_game'), StateFilter(default_state))
async def process_create_game_command(message: Message, state: FSMContext):
    await message.answer('Создание игры: введите текст')
    await state.set_state(FSMCreateGame.set_mode)
    print(await state.get_state())


@router.message(StateFilter(FSMCreateGame.set_mode))
async def process_set_game_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)

    await message.answer(
        text='Отлично! Теперь укажите режим игры: ответ кнопками или текстом',
        reply_markup=create_inline_kb(2, {'Кнопки': 'select', 'Текст': 'text'})
    )

    await state.set_state(FSMCreateGame.request_options)
    print(await state.get_state())


@router.callback_query(StateFilter(FSMCreateGame.request_options), F.data.in_(['select']))
async def process_request_select_options(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type=callback.data)
    #await callback.message.delete()
    await callback.message.delete()
    await callback.message.answer(
        text='Класс! Теперь нужно ввести возможные варианты ответов через символ "|", например: Огурец | Николай | Лада 2114'
    )
    await state.set_state(FSMCreateGame.set_options)
    print(await state.get_state())


@router.callback_query(StateFilter(FSMCreateGame.request_options))
async def process_request_text_options(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type=callback.data)
    if callback.data == 'text':
        await state.update_data(options='')
    await callback.message.delete()
    await callback.message.answer(text='Хорошо, теперь нужно ввести правильный вариант ответа')
    await state.set_state(FSMCreateGame.set_answers)
    print(await state.get_state())


@router.message(StateFilter(FSMCreateGame.set_options))
async def process_set_select_options(message: Message, state: FSMContext):
    await state.update_data(options=message.text)
    await message.answer('Хорошо, теперь нужно ввести правильный вариант (или варианты) ответа, также через символ "|"')
    await state.set_state(FSMCreateGame.set_answers)
    print(await state.get_state())


@router.message(StateFilter(FSMCreateGame.set_answers))
async def process_set_answers(message: Message, state: FSMContext):
    await state.update_data(answers=message.text)
    await message.answer('Принято! Теперь нужно указать развёрнутый ответ')
    await state.set_state(FSMCreateGame.set_full_answer)
    print(await state.get_state())


@router.message(StateFilter(FSMCreateGame.set_full_answer))
async def process_set_full_answer(message: Message, state: FSMContext):
    await state.update_data(full_answer=message.text)
    await message.answer('Есть, теперь идентификатор цикла - "once" для единоразовой игры или любой другой для цикла игр')
    await state.set_state(FSMCreateGame.set_sequence_label)
    print(await state.get_state())


@router.message(StateFilter(FSMCreateGame.set_sequence_label))
async def process_set_label(message: Message, state: FSMContext):
    await state.update_data(sequence_label=message.text)

    await message.answer(
        text='Ответ записан! Теперь нужен уникальный идентификатор игры'
    )

    await state.set_state(FSMCreateGame.set_label)
    print(await state.get_state())


@router.message(StateFilter(FSMCreateGame.set_label))
async def process_set_label(message: Message, state: FSMContext):
    await state.update_data(label=message.text)

    

    await state.set_state(FSMCreateGame.get_final_message)
    print(await state.get_state())


@router.message(StateFilter(FSMCreateGame.get_final_message))
async def process_get_final_message(message: Message, state: FSMContext):
    await state.update_data(final_message=message.text)
    await message.answer(
        text='Отлично! Теперь нужно загрузить картинки для игры, когда все картинки будут загружены, нажмите на кнопку',
        reply_markup=create_inline_kb(1, {'Готово': 'images_uploaded'})
    )
    await state.set_state(FSMCreateGame.upload_pictures)
    print(await state.get_state())


@router.message(StateFilter(FSMCreateGame.upload_pictures), F.photo)
async def process_upload_pictures(message: Message, state: FSMContext):
    try:
        images = (await state.get_data())['images']
    except:
        images = ''
    if images == '':
        await state.update_data(images=message.photo[-1].file_id)
    else:
        await state.update_data(images=images + '|' + message.photo[-1].file_id)
    print(await state.get_state())


@router.callback_query(StateFilter(FSMCreateGame.upload_pictures))
async def process_finishing_uploading_pictures(callback: CallbackQuery, state: FSMContext):
    print(await state.get_data())
    game = Game(**await state.get_data())
    save_game(game)
    print(game)
    await state.clear()
    print(await state.get_state())
    await callback.message.delete()
    await callback.message.answer(text='Поздравляю, игра создана!')


@router.message(StateFilter(default_state), Command(commands='launch_game'))
async def process_schedule_game(message: Message, state: FSMContext):
    await message.answer('Для запуска введите уникальный идентификатор игровой последовательности')
    await state.set_state(FSMScheduleGame.get_sequence_label)
    print(await state.get_state())


@router.message(StateFilter(FSMScheduleGame.get_sequence_label))
async def process_get_label(message: Message, state: FSMContext):
    await state.update_data(sequence_label=message.text)
    
    await message.answer(
        text='Запустить игру сейчас?',
        reply_markup=create_inline_kb(2, {'Запуск': 'run', 'Тест': 'test', 'Отмена': 'cancel'})
    )
    await state.set_state(FSMScheduleGame.run)
    print(await state.get_state())


@router.callback_query(StateFilter(FSMScheduleGame.run))
async def process_get_label(callback: CallbackQuery, state: FSMContext, bot: Bot):
    sequence_label = (await state.get_data())['sequence_label']
    game: Game = get_game(sequence_label=sequence_label)
    print(game)
    
    if callback.data in ['run', 'test']:
        await callback.message.delete()
        await callback.message.answer(text='Игра запущена!')

        game_callback = GameCallback(
            sequence_label=game.sequence_label,
            type=game.type
        ).pack()
        
        if callback.data == 'test':
            users = get_users(is_admin=True)
        else:
            users = get_users()
        print(users)
        for user in users:
            try:
                if user.last_call != "" and user.last_call != None:
                    print('ЖОПА ОЧКА')
                    continue
                msg = await bot.send_message(
                    chat_id=user.user_id,
                    text='Давай поиграем?',
                    reply_markup=create_inline_kb(1, {'Начать': game_callback})
                )
                msg_id=msg.message_id
                msg_date=msg.date.isoformat()
                msg_chat_id=msg.chat.id
                msg_chat_type=msg.chat.type
                update_user(user.user_id, {'last_call': f'{msg_id}|{msg_date}|{msg_chat_id}|{msg_chat_type}'})
            except:
                print("МЫ В ДЕРЬМЕ!!!!!!!!!!!!!!!!!!!!")
        await state.clear()
    else:
        await callback.message.delete()
        await callback.message.answer(text='Запуск игры отменён')
        await state.clear()

@router.message(StateFilter(default_state), Command(commands='stop_game'))
async def process_stop_game_command(message: Message, state: FSMContext):
    await message.answer('Введите идентификатор последовательности')
    await state.set_state(FSMStopGame.get_label)
    print(await state.get_state())


@router.message(StateFilter(FSMStopGame.get_label))
async def process_stop_game_command(message: Message, bot: Bot, state: FSMContext):
    await message.answer('Введите сообщение для отправки по окончании игры')
    await state.update_data({'sequence_label': message.text})
    await state.set_state(FSMStopGame.stop)
    print(await state.get_state())
    

@router.message(StateFilter(FSMStopGame.stop))
async def process_stop_game_get_label(message: Message, bot: Bot, state: FSMContext):
    sequence_label = (await state.get_data())['sequence_label']
    users = get_users()
    participants = set([x.username for x in get_game_results(sequence_label=sequence_label)])
    for user in users:
        print(user.username, user.last_call)
        #if user.last_call != None and user.last_call != '':
        if user.username in participants:
            try:
                msg: Message = await message.send_copy(chat_id=user.user_id)
                # await msg.delete()
            except:
                # print('Exception: Cannot delete non-existing message')
                print('Exception: bot blocked by user')
            finally:
                update_user(user.user_id, {'last_call': None})
            # await bot.send_message(
            #     chat_id=user.user_id,
            #     text='Спасибо за участие в игре!\nСкоро Бо подведёт итоги и назовёт победителя 🏆'
            # )
            try:
                if msg.text != 'Давай поиграем?':
                    await message.send_copy(chat_id=user.user_id)
            except:
                print('Exception: Bot most likely was blocked by the user')
            

    await message.answer('Игра остановлена!')
    await state.clear()
    print(await state.get_state())


# @router.message(StateFilter(default_state), Command(commands='stop_game_test'))
# async def process_stop_game_command(message: Message, bot: Bot):
    # users = get_users(is_admin=True)
    # for user in users:
    #     print(user.username, user.last_call)
    #     if user.last_call != '':
    #         msg_list = user.last_call.split('|')
    #         msg: Message = Message(
    #             message_id=msg_list[0],
    #             date=msg_list[1],
    #             chat=Chat(id=msg_list[2], type=msg_list[3])
    #         ).as_(bot)
    #         await msg.delete()
    #         update_user(user.user_id, {'last_call': ''})
            
    #     else:
    #         await bot.send_message(
    #             chat_id=user.user_id,
    #             text='Спасибо за участие в игре!\nСкоро Бо подведёт итоги и назовёт победителя 🏆'
    #         )

    # await message.answer('Игра остановлена!')


@router.message(StateFilter(default_state), Command(commands='get_results'))
async def process_get_results_command(message: Message, state: FSMContext):
    await message.answer('Для получения результатов отправьте идентификатор игровой последовательности')
    await state.set_state(FSMGetGameResults.get_label)
    print(await state.get_state())


@router.message(StateFilter(FSMGetGameResults.get_label))
async def get_game_results_get_label(message: Message, state: FSMContext):
    game_results = get_game_results(sequence_label=message.text)
    if len(game_results) == 0:
        message.answer('Результатов не найдено')
        await state.clear()
        print(await state.get_state())
    else:
        answer = []
        for game_result in game_results:
            answer.append('@' + game_result.username + ' ✅' if game_result.is_correct else ' ❌')
        await message.answer('\n'.join(answer))
    await state.clear()
    print(await state.get_state())


@router.message(StateFilter(default_state), Command(commands='giveaway'))
async def process_giveaway_command(message: Message, state: FSMContext):
    await message.answer('Запуск розыгрыша: введите уникальный идентификатор')
    await state.set_state(FSMScheduleGiveaway.get_label)
    print(await state.get_state())


@router.message(StateFilter(FSMScheduleGiveaway.get_label))
async def process_giveaway_command(message: Message, state: FSMContext):
    await state.update_data(label=message.text)

    await message.answer('Теперь нужно задать таймфрейм отправки сообщения: введите datetime в iso-формате и через | продолжительность в минутах (например, 2023-12-01T20:26|180)')
    await state.set_state(FSMScheduleGiveaway.get_time)
    print(await state.get_state())


@router.message(StateFilter(FSMScheduleGiveaway.get_time))
async def get_giveaway_time(message: Message, state: FSMContext):
    try:
        dt, tf = message.text.split('|')
        time_start = datetime.fromisoformat(dt)
        time_stop = time_start + timedelta(minutes=int(tf))
        await state.update_data(time_start=time_start.isoformat(), time_stop=time_stop.isoformat())
        await message.answer('Принято! Теперь сообщение, которое нужно отправить')
        await state.set_state(FSMScheduleGiveaway.get_message)
    except:
        await message.answer('Что-то пошло не так, попробуйте снова')
    print(await state.get_state())


async def jobfunc(message: Message, bot: Bot, label):
    users = get_users()
    markup=create_inline_kb(1, {'Участвовать!': GiveawayCallback(label=label).pack()})
    for user in users:
        print(user.username, user.last_call_giveaway)
        if user.last_call_giveaway == None or user.last_call_giveaway == '':
            print(user.last_call_giveaway)
            try:
                msg: Message = await message.send_copy(chat_id=user.user_id, reply_markup=markup)
                msg_id=msg.message_id
                msg_date=msg.date.isoformat()
                msg_chat_id=msg.chat.id
                msg_chat_type=msg.chat.type
                update_user(user.user_id, {'last_call_giveaway': f'{msg_id}|{msg_date}|{msg_chat_id}|{msg_chat_type}'})
                
                print(f'Сообщение отправлено пользователю {user.user_id} ({user.username})')
            except:
                print(f'Пользователь {user.user_id} ({user.username}) заблокировал бота (мб)')

async def destroy_job(myjob, bot: Bot, label):
    # scheduler.remove_job('myjob_id')
    print('Завершение розыгрыша: ' + datetime.now().isoformat())
    myjob.remove()
    for user in get_users():
        if user.last_call_giveaway != None and user.last_call_giveaway != '':
            try:
                msg_list = user.last_call_giveaway.split('|')
                msg: Message = Message(
                    message_id=msg_list[0],
                    date=msg_list[1],
                    chat=Chat(id=msg_list[2], type=msg_list[3])
                ).as_(bot)
                if not get_giveaway(label=label, user_id=user.user_id):
                    try:
                        await msg.delete()
                    except:
                        print(f'Невозможно удалить сообщение для пользователя {user.user_id} ({user.username})')
                else:
                    await bot.send_message(
                        chat_id=user.user_id,
                        text='Спасибо за участие в розыгрыше! Скоро Бо подведёт итоги!'
                    )
            except:
                print(f'Пользователь {user.user_id} ({user.username}) заблокировал бота (мб)')
            finally:
                update_user(user.user_id, {'last_call_giveaway': None})
    
    print('Розыгрыш окончен: ' + datetime.now().isoformat())


@router.message(StateFilter(FSMScheduleGiveaway.get_message))
async def get_giveaway_time(message: Message, state: FSMContext, bot=Bot):
    time_start = datetime.fromisoformat((await state.get_data())['time_start'])
    time_stop = datetime.fromisoformat((await state.get_data())['time_stop'])
    label = (await state.get_data())['label']
    myjob = scheduler.add_job(jobfunc, 'interval', seconds=15, args=[message, bot, label])
    print(time_stop)
    scheduler.add_job(destroy_job, 'date', run_date=time_stop, args=[myjob, bot, label])
    await message.answer('Готово!')
    await state.clear()
    print(await state.get_state())


@router.message(StateFilter(default_state), Command(commands='message_users'))
async def process_message_users_command(message: Message, state: FSMContext):
    await message.answer('Я перешлю всем пользователям следующее сообщение, которое вы мне пришлёте. Для отмены используйте команду /cancel')
    await state.set_state(FSMMessageUsers.get_text)
    print(await state.get_state())


@router.message(StateFilter(FSMMessageUsers.get_text))
async def get_message_to_user_text(message: Message, bot: Bot, state: FSMContext):
    for user in get_users():
        try:
            await message.send_copy(chat_id=user.user_id)
        except:
            print(f'PENCIL ALARM {user.username} ({user.user_id})')
    await message.answer('Сообщение отправлено!')
    await state.clear()
    print(await state.get_state())

@router.message(StateFilter(default_state), Command(commands='message_user'))
async def process_message_user_command(message: Message, state: FSMContext):
    await message.answer('Для отправки сообщения пользователю мне нужен его username, например, @maks9804.\nДля отмены используйте команду /cancel')
    await state.set_state(FSMMessageUser.get_username)
    print(await state.get_state())

@router.message(StateFilter(FSMMessageUser.get_username))
async def get_message_to_user_user(message: Message, state: FSMContext):
    await state.update_data(username=message.text[1:])
    print(message.text[1:])
    await message.answer('Я перешлю пользователю следующее сообщение, которое вы мне пришлёте.\nДля отмены используйте команду /cancel')
    await state.set_state(FSMMessageUser.get_text)
    print(await state.get_state())


@router.message(StateFilter(FSMMessageUser.get_text))
async def get_message_to_user_text(message: Message, bot: Bot, state: FSMContext):
    username = (await state.get_data())['username']
    print(f'{username=}')
    print(f'{get_user_by_username(username).user_id=}')
    await message.send_copy(chat_id=get_user_by_username(username).user_id)
    await message.answer('Сообщение отправлено!')
    await state.clear()
    print(await state.get_state())


@router.message(Command(commands='get_user_count'), StateFilter(default_state))
async def process_list_users_command(message: Message):
    await message.answer(str(len(get_users())))
    #arstarstarstarstarst
    # await message.answer('\n'.join([f'Имя: {user.name}\nПрофиль: @{user.username}\nТелефон: {user.phone}\nID: {user.user_id}\nБаллы: {user.points}\n' for user in get_users()]))


@router.message(Command(commands='echo'), StateFilter(default_state))
async def process_echo_command(message: Message, state: FSMContext):
    await state.set_state(FSMEchoPost.get_buttons)
    await message.answer('Отправьте кнопку в формате ТЕКСТ | URL, если она нужна, и "-" в противном случае')


@router.message(StateFilter(FSMEchoPost.get_buttons))
async def echo_get_buttons(message: Message, state: FSMContext):
    await state.update_data(urls=message.text)
    await state.set_state(FSMEchoPost.get_channel)
    await message.answer('Хорошо, теперь название канала, куда нужно сделать пост')
    print(await state.get_state())


@router.message(StateFilter(FSMEchoPost.get_channel))
async def echo_get_channel(message: Message, state: FSMContext):
    await state.update_data(channel=message.text)
    await message.answer('Принято. Теперь сам пост')
    await state.set_state(FSMEchoPost.echo)
    print(await state.get_state())

@router.message(StateFilter(FSMEchoPost.echo))
async def process_echo_post(message: Message, bot: Bot, state: FSMContext):
    urls = (await state.get_data())['urls']
    channel = (await state.get_data())['channel']
    markup = None
    if urls != '-':
        text = urls.split('|')[0].strip()
        url = urls.split('|')[1].strip()
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, url=url)]])
    await bot.copy_message(
        message_id=message.message_id,
        from_chat_id=message.from_user.id,
        chat_id=channel,
        reply_markup=markup
    )
    await message.answer('Готово!')
    await state.clear()
    print(await state.get_state())


@router.message(Command(commands='add_promo'), StateFilter(default_state))
async def process_add_promo(message: Message, state: FSMContext):
    await message.answer(LEXICON['admin_save_promo_get_label'])
    await state.set_state(FSMSavePromo.get_label)
    print(await state.get_state())


@router.message(StateFilter(FSMSavePromo.get_label))
async def add_promo_get_label(message: Message, state: FSMContext):
    await message.answer(LEXICON['admin_save_promo_get_image'])
    await state.update_data(label=message.text)
    await state.set_state(FSMSavePromo.save)
    print(await state.get_state())


@router.message(StateFilter(FSMSavePromo.save))
async def process_save_promo(message: Message, state: FSMSavePromo):
    promo = Promo(
        label=(await state.get_data())['label'],
        description=message.caption,
        image=message.photo[-1].file_id,
        status='inactive'
    )
    save_promo(promo)
    await message.answer(LEXICON['admin_save_promo_ok'])
    await state.clear()
    print(await state.get_state())


@router.message(Command(commands='edit_promos'))
async def process_edit_promos(message: Message, state: FSMContext):
    promos = get_promos()
    buttons = {promo.label: promo.label for promo in promos}
    buttons.update({'Выход': 'exit'})
    markup = create_inline_kb(1, buttons)
    msg: Message = await message.answer(LEXICON['admin_edit_promos'], reply_markup=markup)

    await state.update_data(
        msg_id=msg.message_id,
        msg_date=msg.date.isoformat(),
        msg_chat_id=msg.chat.id,
        msg_chat_type=msg.chat.type
    )
    await state.set_state(FSMEditPromos.select)


@router.callback_query(StateFilter(FSMEditPromos.select))
async def edit_promos_select(callback: CallbackQuery, state: FSMContext, bot: Bot):
    msg_id = (await state.get_data())['msg_id']
    msg_date = datetime.fromisoformat((await state.get_data())['msg_date'])
    msg_chat = Chat(id=(await state.get_data())['msg_chat_id'], type=(await state.get_data())['msg_chat_type'])
    msg: Message = Message(
        message_id=msg_id,
        date=msg_date,
        chat=msg_chat
    ).as_(bot)
    if callback.data == 'exit':
        await msg.delete()
        await state.clear()
        print(await state.get_state())
    else:
        print(callback.data)
        promo_status = 'активен' if get_promo(callback.data).label == 'active' else 'неактивен'
        msg.edit_text(f'Вы выбрали промо-код {callback.data}, сейчас он {promo_status}')
        await state.update_data(selected_promo=callback.data)
        toggle_btn = 'Деактивировать' if get_promo(callback.data).status == 'active' else 'Активировать'
        markup = create_inline_kb(1, {
            toggle_btn: 'toggle', 
            'Удалить': 'delete', 
            'Вернуться к списку': 'back_to_list', 
            'Выход': 'exit'
        })
        await msg.edit_text(f'Выбран промокод: {get_promo(callback.data).label}', reply_markup=markup)
        await state.set_state(FSMEditPromos.choose_action)


@router.callback_query(StateFilter(FSMEditPromos.choose_action))
async def edit_promos_choose_action(callback: CallbackQuery, state: FSMContext, bot: Bot):
    msg_id = (await state.get_data())['msg_id']
    msg_date = datetime.fromisoformat((await state.get_data())['msg_date'])
    msg_chat = Chat(id=(await state.get_data())['msg_chat_id'], type=(await state.get_data())['msg_chat_type'])
    msg: Message = Message(
        message_id=msg_id,
        date=msg_date,
        chat=msg_chat
    ).as_(bot)
    promo_label: str = (await state.get_data())['selected_promo']
    if callback.data == 'exit':
        await msg.delete()
        await state.clear()
        print(await state.get_state())
    elif callback.data == 'toggle':
        toggle_promo(promo_label)
        toggle_btn = 'Деактивировать' if get_promo(promo_label).status == 'active' else 'Активировать'
        markup = create_inline_kb(1, {
            toggle_btn: 'toggle', 
            'Удалить': 'delete', 
            'Вернуться к списку': 'back_to_list', 
            'Выход': 'exit'
        })
        await msg.edit_reply_markup(reply_markup=markup)
    elif callback.data == 'delete':
        delete_promo(promo_label)
        await callback.answer(text='Промо-код удалён, возврат к списку кодов...', show_alert=True)
        promos = get_promos()
        buttons = {promo.label: promo.label for promo in promos}
        buttons.update({'Выход': 'exit'})
        markup = create_inline_kb(1, buttons)
        await msg.edit_text(LEXICON['admin_edit_promos'], reply_markup=markup)
        await state.set_state(FSMEditPromos.select)
    elif callback.data == 'back_to_list':
        promos = get_promos()
        buttons = {promo.label: promo.label for promo in promos}
        buttons.update({'Выход': 'exit'})
        markup = create_inline_kb(1, buttons)
        await msg.edit_text(LEXICON['admin_edit_promos'], reply_markup=markup)
        await state.set_state(FSMEditPromos.select)
        print(await state.get_state())