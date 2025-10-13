from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from lexicon.lexicon_ru import LEXICON
from states.states import FSMRegister
from models.methods import save_user, get_user, update_user
from models.models import User
from keyboards.keyboard_utils import create_inline_kb, phone_kb
from handlers.utils import format_number


router = Router()


@router.message(Command(commands="register"), StateFilter(default_state))
async def process_register_command(message: Message):
    if get_user(message.from_user.id):
        await message.answer(
            text="Вы уже зарегистрированы, уверены, что хотите пройти процесс заново?",
            reply_markup=create_inline_kb(
                2, {"Да": "perform_registration", "Отмена": "cancel_registration"}
            ),
        )
    else:
        await message.answer(
            text="Мне нужны некоторые данные, чтобы вы могли поучаствовать в играх, давайте их заполним?",
            reply_markup=create_inline_kb(
                2, {"Да": "perform_registration", "Отмена": "cancel_registration"}
            ),
        )


@router.callback_query(
    StateFilter(default_state),
    F.data.in_(["perform_registration", "cancel_registration"]),
)
async def process_register_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data == "perform_registration":
        await callback.message.answer(LEXICON["user_registration_request_name"])
        await state.set_state(FSMRegister.set_name)
    await callback.answer()
    await callback.message.delete()


@router.message(StateFilter(FSMRegister.set_name), F.text)
async def process_set_name(message: Message, state: FSMContext):
    await state.update_data(username=message.from_user.username)
    await message.answer(
        LEXICON["user_registration_request_phone_number"] % message.text,
        reply_markup=phone_kb(),
    )
    await state.update_data(name=message.text)
    await state.update_data(mail="-")
    await state.set_state(FSMRegister.set_phone)


@router.message(StateFilter(FSMRegister.set_name), ~F.text)
async def process_set_name_error(message: Message):
    await message.answer(LEXICON["dont_understand"])


@router.message(StateFilter(FSMRegister.set_phone), F.contact)
async def process_set_phone(message: Message, state: FSMContext):
    contact = message.contact

    if contact.user_id and contact.user_id != message.from_user.id:
        await message.answer(
            "Please share **your** phone using the button.", reply_markup=phone_kb()
        )
        return

    phone = contact.phone_number

    await state.update_data(phone=phone)
    await message.answer(
        LEXICON["user_registration_phone_number_accepted"],
        reply_markup=ReplyKeyboardRemove(),
    )

    phone = format_number(phone)

    await state.update_data(phone=phone)
    user = get_user(message.from_user.id)

    if user:
        await state.update_data(points=user.points)
        await state.update_data(is_admin=user.is_admin)
        update_user(message.from_user.id, await state.get_data())
    else:
        await state.update_data(points=0)
        await state.update_data(is_admin=False)
        await state.update_data(user_id=message.from_user.id)
        save_user(User(**await state.get_data()))

    await message.answer(LEXICON["user_registration_greeting"])
    await state.clear()


@router.message(StateFilter(FSMRegister.set_phone), ~F.text)
async def process_set_phone_error(message: Message):
    await message.answer(LEXICON["dont_understand"])
