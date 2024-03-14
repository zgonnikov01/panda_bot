from aiogram.fsm.state import StatesGroup, State


class FSMCreateGame(StatesGroup):
    set_text = State()
    set_mode = State()
    request_options = State()
    set_options = State()
    set_answers = State()
    set_label = State()
    set_sequence_label = State()
    upload_pictures = State()
    set_full_answer = State()
    get_final_message = State()
    

class FSMLoadJsonGame(StatesGroup):
    set_sequence_label = State()
    load_json = State()
    load_pictures = State()
    save = State()


class FSMScheduleGame(StatesGroup):
    start = State()
    get_sequence_label = State()
    run = State()


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
    