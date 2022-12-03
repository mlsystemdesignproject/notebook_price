import requests
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from client_states import DialogueStates
from keyboards import get_reply_keyboard_markup
from messages_for_main_menu import text_output_for_command
from possible_answers import choices_per_stage, all_processors_regexp, hdmi_port_answers
from json.decoder import JSONDecodeError
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')
API_URL = 'https://njs0kuvzkj.execute-api.us-west-1.amazonaws.com/prod/predict-price'

bot = Bot(token=token)
dispatcher = Dispatcher(bot, storage=MemoryStorage())
ML_APP_URL = 'http://127.0.0.1:8000/get_model_prediction'


@dispatcher.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await bot.send_message(
        text='Welcome to our bot!',
        chat_id=message.from_user.id,
        reply_markup=get_reply_keyboard_markup(['/estimate', '/help', '/about']),
    )
    await message.delete()
    await DialogueStates.MAIN_MENU.set()


@dispatcher.message_handler(commands=list(text_output_for_command.keys()), state=DialogueStates.MAIN_MENU)
async def html_out_command(message: types.Message):
    """Выводит информацию в виде HTML."""
    await bot.send_message(
        text=text_output_for_command[message.text[1:]],
        chat_id=message.from_user.id,
        parse_mode='HTML',
    )
    await message.delete()


@dispatcher.message_handler(commands=['estimate'], state=DialogueStates.MAIN_MENU)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.PROCESSOR_BRAND.set()

    await bot.send_message(
        text='Выберите бренд вашего ноутбука',
        chat_id=message.from_user.id,
        reply_markup=get_reply_keyboard_markup(
            choices_per_stage[await state.get_state()]
        )
    )
    await message.delete()


@dispatcher.message_handler(
    regexp='|'.join(choices_per_stage[DialogueStates.PROCESSOR_BRAND.state]),
    state=DialogueStates.PROCESSOR_BRAND,
)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.PROCESSOR_SERIES.set()
    async with state.proxy() as data:
        data['processor_brand'] = message.text
    await bot.send_message(
        text='Выберите семейство вашего процессора',
        chat_id=message.from_user.id,
        reply_markup=get_reply_keyboard_markup(
            choices_per_stage[await state.get_state() + f"_{'Apple' if message.text == 'Apple' else 'Other'}"]
        )
    )
    await message.delete()


@dispatcher.message_handler(
    regexp=all_processors_regexp,
    state=DialogueStates.PROCESSOR_SERIES,
)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.PROCESSOR_CORES.set()
    async with state.proxy() as data:
        data['processor_series'] = message.text
        print(data)
    await bot.send_message(
        text='Введите количество ядер процессора (от 1 до 14)',
        chat_id=message.from_user.id,
        reply_markup=None,
    )
    await message.delete()


@dispatcher.message_handler(
    lambda message: message.text.isdigit() and 0 < int(message.text) < 15,
    state=DialogueStates.PROCESSOR_CORES,
)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.VIDEOCARD_TYPE.set()
    async with state.proxy() as data:
        data['processor_cores'] = int(message.text)
        print(data)
    await bot.send_message(
        text='Выберите производителя видеокарты',
        chat_id=message.from_user.id,
        reply_markup=get_reply_keyboard_markup(
            choices_per_stage[await state.get_state()]
        )
    )
    await message.delete()


@dispatcher.message_handler(state=DialogueStates.PROCESSOR_CORES)
async def retry_processor_cores(message: types.Message):
    await bot.send_message(
        text='Неверный формат числа! Введите количество ядер процессора (от 1 до 14)',
        chat_id=message.from_user.id,
    )


@dispatcher.message_handler(
    regexp='|'.join(choices_per_stage[DialogueStates.VIDEOCARD_TYPE.state]),
    state=DialogueStates.VIDEOCARD_TYPE,
)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.VIDEOCARD_MEMORY.set()
    async with state.proxy() as data:
        data['videocard_type'] = message.text
        if message.text == 'интегрированная':
            # Для интегрированной видеокарты нет памяти
            data['videocard_memory'] = 0
            await DialogueStates.SCREEN_DIAGONAL.set()
            await bot.send_message(
                text='Введите размер диагонали экрана в дюймах (от 10 до 17)',
                chat_id=message.from_user.id,
            )
            return
    await bot.send_message(
        text='Введите количество видеопамяти в ГБ (от 1 до 16)',
        chat_id=message.from_user.id,
    )
    await message.delete()


@dispatcher.message_handler(
    lambda message: message.text.isdigit() and 0 < int(message.text) < 17,
    state=DialogueStates.VIDEOCARD_MEMORY,
)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.SCREEN_DIAGONAL.set()
    async with state.proxy() as data:
        data['videocard_memory'] = int(message.text)
        print(data)
    await bot.send_message(
        text='Введите размер диагонали экрана в дюймах (от 10 до 17)',
        chat_id=message.from_user.id,
    )
    await message.delete()


@dispatcher.message_handler(state=DialogueStates.VIDEOCARD_MEMORY)
async def retry_videocard_memory(message: types.Message):
    await bot.send_message(
        text='Неверный формат числа! Введите количество видеопамяти в ГБ (от 1 до 16)',
        chat_id=message.from_user.id,
    )


@dispatcher.message_handler(
    lambda message: message.text.isdigit() and 0 < int(message.text) < 18,
    state=DialogueStates.SCREEN_DIAGONAL,
)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.SSD_VOLUME.set()
    async with state.proxy() as data:
        data['screen_diagonal'] = float(message.text)
        print(data)
    await bot.send_message(
        text='Введите размер SSD диска в ГБ (если его не должно быть - введите 0)',
        chat_id=message.from_user.id,
    )
    await message.delete()


@dispatcher.message_handler(state=DialogueStates.SCREEN_DIAGONAL)
async def retry_screen_diagonal(message: types.Message):
    await bot.send_message(
        text='Неверный формат числа! Введите размер диагонали экрана в дюймах (от 10 до 17)',
        chat_id=message.from_user.id,
    )


@dispatcher.message_handler(
    lambda message: message.text.isdigit() and 0 <= int(message.text) < 8193,
    state=DialogueStates.SSD_VOLUME,
)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.RAM_VOLUME.set()
    async with state.proxy() as data:
        data['ssd_volume'] = int(message.text)
        print(data)
    await bot.send_message(
        text='Введите объем оперативной памяти в ГБ (от 2 до 64)',
        chat_id=message.from_user.id,
    )
    await message.delete()


@dispatcher.message_handler(state=DialogueStates.SSD_VOLUME)
async def retry_screen_diagonal(message: types.Message):
    if message.text.isdigit():
        if int(message.text) > 8192:
            await bot.send_message(
                text='8ТБ конечно круто, но пока таких ноутов нет) Введи меньший объем диска!',
                chat_id=message.from_user.id,
            )
        else:
            await bot.send_message(
                text='Отрицательная память?) Ну ты загнул)) Введи число от 0 до 8192 (ГБ)',
                chat_id=message.from_user.id,
            )
    else:
        await bot.send_message(
            text='Неверный формат числа! Введите размер SSD диска в ГБ (если его не должно быть - введите 0)',
            chat_id=message.from_user.id,
        )


@dispatcher.message_handler(
    lambda message: message.text.isdigit() and 0 <= int(message.text) < 65,
    state=DialogueStates.RAM_VOLUME,
)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.HDMI_PORT.set()
    async with state.proxy() as data:
        data['ram_volume'] = int(message.text)
        print(data)
    await bot.send_message(
        text='Нужен ли тебе HDMI порт?',
        chat_id=message.from_user.id,
        reply_markup=get_reply_keyboard_markup(
            choices_per_stage[await state.get_state()]
        )
    )
    await message.delete()


@dispatcher.message_handler(state=DialogueStates.RAM_VOLUME)
async def retry_ram_volume(message: types.Message):
    await bot.send_message(
        text='Неверный формат числа! Введите объем оперативной памяти в ГБ (от 2 до 64)',
        chat_id=message.from_user.id,
    )


@dispatcher.message_handler(
    regexp='|'.join(choices_per_stage[DialogueStates.HDMI_PORT.state]),
    state=DialogueStates.HDMI_PORT,
)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.MATERIAL.set()
    async with state.proxy() as data:
        print(message.text)
        data['hdmi_port'] = hdmi_port_answers[message.text]
    await bot.send_message(
        text='Выберите материал корпуса вашего ноута',
        chat_id=message.from_user.id,
        reply_markup=get_reply_keyboard_markup(
            choices_per_stage[await state.get_state()]
        )
    )
    await message.delete()


@dispatcher.message_handler(
    regexp='|'.join(choices_per_stage[DialogueStates.MATERIAL.state]),
    state=DialogueStates.MATERIAL,
)
async def estimate_command(message: types.Message, state: FSMContext):
    await DialogueStates.BATTERY_LIFE.set()
    async with state.proxy() as data:
        data['material'] = message.text
    await bot.send_message(
        text='Выберите желаемую продолжительность автономной работы в часах (от 3 до 29)',
        chat_id=message.from_user.id,
    )
    await message.delete()


@dispatcher.message_handler(
    lambda message: message.text.isdigit() and 3 <= int(message.text) < 30,
    state=DialogueStates.BATTERY_LIFE,
)
async def estimate_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['battery_life'] = int(message.text)
        features = ''
        for key, value in data.items():
            features += f'{key} = {value}\n'
        print(data.as_dict())
        try:
            prices = requests.post(
                url=API_URL,
                json=data.as_dict(),
                headers={'x-api-key': API_KEY},
            ).json()
        except JSONDecodeError:
            return
        price_str = f'от {prices["min_price"]:.0f} до {prices["max_price"]:.0f} рублей.'
        features += f'Ноутбук с вышеуказанными характеристиками стоит ' + price_str
        await bot.send_message(
            text=features,
            chat_id=message.from_user.id,
        )
        await DialogueStates.MAIN_MENU.set()
    await message.delete()


@dispatcher.message_handler(state=DialogueStates.BATTERY_LIFE)
async def retry_ram_volume(message: types.Message):
    await bot.send_message(
        text='Неверный формат числа! Выберите желаемую продолжительность автономной работы в часах (от 3 до 29)',
        chat_id=message.from_user.id,
    )


@dispatcher.message_handler(commands=['restart'], state='*')
async def estimate_command(message: types.Message):
    await DialogueStates.MAIN_MENU.set()
    await bot.send_message(
        text='Welcome to our bot!',
        chat_id=message.from_user.id,
        reply_markup=get_reply_keyboard_markup(['/estimate', '/help', '/about']),
    )


if __name__ == '__main__':
    executor.start_polling(dispatcher)
