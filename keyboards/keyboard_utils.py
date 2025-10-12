from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_kb(width: int,
                     keys: dict,
                     last_btn: dict = None) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    if keys:
        for text, button in keys.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button
            ))

    kb_builder.row(*buttons, width=width)
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=list(last_btn.keys())[0],
            callback_data=list(last_btn.values())[0]
        ))

    return kb_builder.as_markup()


def phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Share my phone", request_contact=True)],
            [KeyboardButton(text="Skip")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        selective=True,
        input_field_placeholder="Tap the button to share your phone"
    )

