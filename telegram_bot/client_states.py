from aiogram.dispatcher.filters.state import State, StatesGroup


class DialogueStates(StatesGroup):
    """Состояния бота в режиме конечных автоматов"""
    MAIN_MENU = State()
    PROCESSOR_BRAND = State()
    PROCESSOR_SERIES = State()
    PROCESSOR_CORES = State()
    VIDEOCARD_TYPE = State()
    VIDEOCARD_MEMORY = State()
    SCREEN_DIAGONAL = State()
    SSD_VOLUME = State()
    RAM_VOLUME = State()
    HDMI_PORT = State()
    MATERIAL = State()
    BATTERY_LIFE = State()
    FEATURES_COLLECTED = State()
    ANSWER_GIVEN = State()
