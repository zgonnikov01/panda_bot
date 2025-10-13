import asyncio
from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.types.chat import Chat
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from config_data.config import config
from lexicon.lexicon_ru import LEXICON
from models.methods import (
    get_user,
    get_game,
    get_promos,
    save_game_result,
    save_giveaway,
)
from models.models import Game, GameResult, Giveaway
from handlers.admin_handlers import GameCallback, GiveawayCallback
from states.states import FSMInGame
from keyboards.set_menu import set_user_menu
from keyboards.keyboard_utils import create_inline_kb


router = Router()


@router.message(
    CommandStart(), lambda message: message.from_user.id not in config.tg_bot.admin_ids
)
async def process_start_command(message: Message, bot: Bot, state: FSMContext):
    await message.answer(LEXICON["user_start"])
    await set_user_menu(message.from_user.id, bot)
    print(message.from_user.id)


@router.callback_query(GiveawayCallback.filter(), StateFilter(default_state))
async def process_start_giveaway_check_subscriptions(
    query: CallbackQuery, callback_data: GameCallback, bot: Bot, state: FSMContext
):
    user_id = query.message.chat.id

    channels = [
        "@pandamarket_club",
        #'@avtoprokat_26reg'
        # "@pencil_alarm"
    ]
    not_subscribed = []

    for channel in channels:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if member.status not in ("member", "administrator", "creator"):
            not_subscribed.append(channel)

    try:
        notify_msg_id = (await state.get_data())["notify_msg_id"]
        if notify_msg_id != None:
            await bot.delete_message(chat_id=user_id, message_id=notify_msg_id)
    except:
        pass

    if not_subscribed:
        channels_list = "\n".join([f"- {ch}" for ch in not_subscribed])
        notify_msg = await query.message.answer(
            f"⚠️ Ты не подписался на каналы, чтобы поучаствовать в розыгрыше, подпишись и нажми на кнопку снова:\n\n"
            f"{channels_list}"
        )
        notify_msg_id = notify_msg.message_id
        await state.update_data(notify_msg_id=notify_msg_id)
        await query.answer()
    else:
        label = callback_data.label
        save_giveaway(
            Giveaway(
                user_id=query.message.chat.id,
                username=query.message.chat.username,
                label=label,
            )
        )
        await query.message.answer("Бо зарегистрировал тебя для участия в розыгрыше!")
        await query.answer()
        await state.update_data(notify_msg_id=None)
        await state.clear()

        user = get_user(query.message.chat.id)
        msg_list = user.last_call_giveaway.split("|")
        msg: Message = Message(
            message_id=msg_list[0],
            date=msg_list[1],
            chat=Chat(id=msg_list[2], type=msg_list[3]),
        ).as_(bot)
        try:
            await msg.delete_reply_markup()
        except:
            print("Exception: Cannot delete non-existing message")


@router.callback_query(
    StateFilter(default_state), GameCallback.filter(F.type == "select")
)
async def process_start_game_select(
    query: CallbackQuery, callback_data: GameCallback, bot: Bot, state: FSMContext
):
    round = 1
    await state.update_data(round=round)
    game = get_game(label=callback_data.sequence_label + f"-{round}")
    images = game.images.split("|")
    await bot.send_media_group(
        chat_id=int(query.message.chat.id),
        media=[InputMediaPhoto(media=images[0], caption=game.text)]
        + [InputMediaPhoto(media=url) for url in images[1:]],
    )

    if len(game.answers.split("|")) > 1:
        await state.set_state(FSMInGame.multiple)

        markup = create_inline_kb(
            1,
            {
                option.strip(): str(i)
                for i, option in enumerate(game.options.split("|"))
            },
            last_btn={"Подтвердить": "CONFIRM"},
        )

        await bot.send_message(
            chat_id=query.message.chat.id,
            text="Выберите один или несколько вариантов ответа, а затем нажмите на кнопку подтверждения",
            reply_markup=markup,
        )

    else:
        await state.set_state(FSMInGame.single)

        markup = create_inline_kb(
            1,
            {
                option.strip(): str(i)
                for i, option in enumerate(game.options.split("|"))
            },
        )

        msg = await bot.send_message(
            chat_id=query.message.chat.id,
            text="Каким будет ваш ответ?",
            reply_markup=markup,
        )

        await state.update_data(
            msg_id=msg.message_id,
            msg_date=msg.date.isoformat(),
            msg_chat_id=msg.chat.id,
            msg_chat_type=msg.chat.type,
        )

    await query.answer()
    await query.message.delete()
    await state.update_data(sequence_label=callback_data.sequence_label)


@router.callback_query(StateFilter(FSMInGame.single))
async def process_play_game_single(
    callback: CallbackQuery, bot: Bot, state: FSMContext
):
    round = (await state.get_data())["round"]
    game: Game = get_game(
        label=(await state.get_data())["sequence_label"] + f"-{round}"
    )

    msg_id = (await state.get_data())["msg_id"]
    msg_date = datetime.fromisoformat((await state.get_data())["msg_date"])
    msg_chat = Chat(
        id=(await state.get_data())["msg_chat_id"],
        type=(await state.get_data())["msg_chat_type"],
    )
    msg: Message = Message(message_id=msg_id, date=msg_date, chat=msg_chat).as_(bot)
    try:
        msg.edit_reply_markup(reply_markup=None)
    except:
        print("can't remove reply markup from giveaway message")
    # update_user(callback.from_user.id, {'last_call': ''})
    save_game_result(
        game_result=GameResult(
            username=callback.from_user.username,
            label=game.label,
            sequence_label=game.sequence_label,
            is_correct=game.options.split("|")[int(callback.data)]
            in game.answers.split("|"),
        )
    )
    await asyncio.sleep(0.3)
    if game.options.split("|")[int(callback.data)] in game.answers.split("|"):
        await callback.message.answer(LEXICON["user_answer_correct"])
        await asyncio.sleep(0.2)
        await callback.message.answer(game.full_answer)
        # update_user(user_id=callback.from_user.id, updates={'points': get_user(callback.from_user.id).points + 100})

    else:
        await callback.message.answer(LEXICON["user_answer_incorrect"])
        await asyncio.sleep(0.2)
        await callback.message.answer(game.full_answer)
    await callback.answer()
    await msg.edit_reply_markup(None)
    await asyncio.sleep(0.5)
    if get_game(label=game.sequence_label + f"-{round + 1}") != None:
        round += 1
        await state.update_data(round=round)
        game = get_game(label=game.sequence_label + f"-{round}")
        images = game.images.split("|")
        await bot.send_media_group(
            chat_id=int(callback.message.chat.id),
            media=[InputMediaPhoto(media=images[0], caption=game.text)]
            + [InputMediaPhoto(media=url) for url in images[1:]],
        )
        await asyncio.sleep(0.5)
        if len(game.answers.split("|")) > 1:
            await state.set_state(FSMInGame.multiple)

            markup = create_inline_kb(
                1,
                {
                    option.strip(): str(i)
                    for i, option in enumerate(game.options.split("|"))
                },
                last_btn={"Подтвердить": "CONFIRM"},
            )

            await bot.send_message(
                chat_id=callback.message.chat.id,
                text="Выберите один или несколько вариантов ответа, а затем нажмите на кнопку подтверждения",
                reply_markup=markup,
            )

        else:
            await state.set_state(FSMInGame.single)

            markup = create_inline_kb(
                1,
                {
                    option.strip(): str(i)
                    for i, option in enumerate(game.options.split("|"))
                },
            )

            msg = await bot.send_message(
                chat_id=callback.message.chat.id,
                text="Каким будет ваш ответ?",
                reply_markup=markup,
            )

            await state.update_data(
                msg_id=msg.message_id,
                msg_date=msg.date.isoformat(),
                msg_chat_id=msg.chat.id,
                msg_chat_type=msg.chat.type,
            )

        await callback.answer()
        await callback.message.delete()
        await state.update_data(game_label=game.label)
    else:
        await callback.message.answer(
            "🐼 Спасибо за участие в игре!\nСкоро Бо подведёт итоги и мы узнаем, кто сегодня выиграл подарки 🎁 от Панда Маркет!"
        )
        # await callback.message.answer('Вы отлично справились!🥳\n\nЭто нужно отметить🐼☝🏻\n\nПоэтому специально для вас я подготовил крутейший предновогодний промокод:\n✅ TG2324\n\n\n🍕 Пицца 4 сезона ( 25 см) при заказе от 1200 рублей.\n❗️ Не забудьте, промокод действителен до 25.12.2023')
        await state.clear()
    print(await state.get_state())


# @router.callback_query(StateFilter(FSMInGame.multiple))
# async def process_play_game_single(callback: CallbackQuery, bot: Bot, state: FSMContext):
#     game = get_game((await state.get_data())['game_label'])
#     if callback.data in game.answers.split('|'):
#         await message.answer('Your')


@router.message(StateFilter(FSMInGame.text), F.text)
async def process_play_game_text(message: Message, state: FSMContext):
    game: Game = get_game(label=(await state.get_data())["game_label"])
    save_game_result(
        game_result=GameResult(
            username=message.from_user.username,
            label=game.label,
            sequence_label=game.sequence_label,
            is_correct=message.text in game.answers,
        )
    )
    if message.text in game.answers:
        await message.answer("Ответ верный!")
        await message.answer(game.full_answer)
    else:
        await message.answer(
            "К сожалению, вы ответили неправильно(\nНо не нужно расстраиваться, следующая игра совсем скоро!"
        )
        await message.answer(game.full_answer)
    await state.clear()


# @router.callback_query(StateFilter(FSMInGame.multiple), F.data.not_in(['CONFIRM']))
# async def process_play_game_multiple_get_answers(callback: CallbackQuery, state: FSMContext):
#     game = get_game((await state.get_data())['game_label'])
#     print(f'<{callback.data}>')
#     if 'user_answers' not in await state.get_data():
#         await state.update_data(user_answers = [])
#     await state.update_data(user_answers=await state.get_data()['user_answers'] + [callback.message.text])


# @router.callback_query(StateFilter(FSMInGame.multiple))
# async def process_play_game_multiple(callback: CallbackQuery, state: FSMContext):
#     game = get_game((await state.get_data())['label'])
#     print(f'<{callback.data}>')
#     user_answers = await state.get_data['user_answers']
#     if user_answers == [x.strip() for x in game.answers.split('|')]:
#         await callback.message.answer(game.full_answer)
#         await callback.message.answer('Ответ верный! Вам начислены бонусные баллы!')

#         update_user(user_id=callback.from_user.id, updates={'points': get_user(callback.from_user.id).points + 100})
#     else:
#         await callback.message.answer(game.full_answer)
#         await callback.message.answer('К сожалению, вы ответили не правильно(\nНо не нужно расстраиваться, следующая игра совсем скоро!')
#     await callback.answer()
#     await callback.message.edit_reply_markup(None)
#     await state.clear()


# @router.message(StateFilter(default_state), Command(commands='points'))
# async def get_points(message: Message):
#     await message.answer(f'Ваши баллы: {get_user(message.from_user.id).points}')


@router.message(StateFilter(default_state), Command(commands="help"))
async def process_help_command(message: Message):
    await message.answer(LEXICON["user_help"])


@router.message(StateFilter(default_state), Command(commands="info"))
async def process_help_command(message: Message):
    await message.answer(LEXICON["user_panda_info"])


@router.message(StateFilter(default_state), Command(commands="promo"))
async def process_promo_command(message: Message, bot: Bot):
    user = get_user(message.from_user.id)
    if user != None:
        promos = get_promos(active=True)
        if len(promos) == 0:
            await message.answer(LEXICON["promo_no_promos"])
        else:
            await message.answer("Актуальные промокоды от Бо!")
            images = [promo.image for promo in promos]
            print(promos)
            descriptions = [promo.description for promo in promos]
            for promo in promos:
                await bot.send_photo(
                    chat_id=message.from_user.id,
                    photo=promo.image,
                    caption=promo.description,
                )
            # await bot.send_media_group(
            #         chat_id=int(message.from_user.id),
            #         # media=[InputMediaPhoto(media=images[0], caption='Актуальные промо-коды от Бо!')] + \
            #         #                               [InputMediaPhoto(media=url) for url in images[1:]]
            #         media=[InputMediaPhoto(media=url) for url in images]
            # )
    else:
        await message.answer(LEXICON["promo_register_first"])


@router.message(lambda message: message.chat.id not in config.tg_bot.admin_ids)
async def echo(message: Message):
    await message.answer(LEXICON["dont_understand"])
