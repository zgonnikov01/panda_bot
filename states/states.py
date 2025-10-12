from aiogram.fsm.state import StatesGroup, State


class FSMLoadJsonGame(StatesGroup):
    set_sequence_label = State()
    load_json = State()
    load_pictures = State()


class FSMScheduleGame(StatesGroup):
    start = State()
    get_sequence_label = State()
    run = State()


class FSMLaunchGiveaway(StatesGroup):
    get_message = State()


class FSMScheduleGiveaway(StatesGroup):
    get_label = State()
    get_time = State()
    get_message = State()
    confirm = State()


class FSMStopGame(StatesGroup):
    stop = State()
    get_label = State()


class FSMRegister(StatesGroup):
    set_name = State()
    set_phone = State()
    set_mail = State()
    # set_city = State()


class FSMInGame(StatesGroup):
    text = State()
    single = State()
    multiple = State()
    repeat = State()


class FSMPost(StatesGroup):
    post = State()


class FSMEchoPost(StatesGroup):
    echo = State()
    get_buttons = State()
    get_channel = State()


class FSMSavePromo(StatesGroup):
    get_label = State()
    save = State()


class FSMEditPromos(StatesGroup):
    select = State() # Выбор промо-кода из списка
    choose_action = State() # Какое-то действие с промо-кодом


class FSMMessageUsers(StatesGroup):
    get_text = State()


class FSMMessageUser(StatesGroup):
    get_username = State()
    get_text = State()


class FSMGetGameResults(StatesGroup):
    get_label = State()
    

class FSMLotteryUpload(StatesGroup):
    get_json = State()

