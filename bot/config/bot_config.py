import os
from functools import wraps
from pathlib import Path

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from cachetools import TTLCache

from database.db_middleware import check_user_by_tg_id

BASE_DIR = Path(os.path.abspath(__file__)).parent.parent
LOGGER = 'bot.log'

load_dotenv(dotenv_path=fr'bot/config/.env')
ADMIN_ID = os.getenv('ADMIN_ID')
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def antispam(rate: int, interval: int, mess: str = "Слишком много запросов"):
    """A decorator that checks if the user has exceeded the request limit in a given amount of time.
    :param rate: request limit
    :param interval: time interval in seconds
    :param mess: message sent to the user if they have exceeded the request limit
    """

    cache = TTLCache(maxsize=rate, ttl=interval)

    def decorator(func):
        @wraps(func)
        async def wrapped(message: types.Message, state: FSMContext, *args, **kwargs):
            user_id = message.from_user.id

            if user_id in cache:
                if cache[user_id] >= rate:
                    await message.reply(mess)
                    return
                cache[user_id] += 1
            else:
                cache[user_id] = 1

            return await func(message, state, *args, **kwargs)

        return wrapped

    return decorator


def check_user_exists():
    """Checking if the user exists in the database

    :return:
    """

    def decorator(func):
        @wraps(func)
        async def wrapped(message: types.Message, state: FSMContext, *args, **kwargs):
            user_id = message.from_user.id

            if not check_user_by_tg_id(tg_id=user_id):
                keyboard = InlineKeyboardMarkup(resize_keyboard=True)
                keyboard.row(InlineKeyboardButton(
                    'Регистрация',
                    callback_data='registration'))
                keyboard.row(InlineKeyboardButton(
                    'У меня уже есть аккаунт',
                    callback_data='authorization'))
                await message.answer('Здравствуйте, для использования бота необходимо зарегистрироваться',
                                     reply_markup=keyboard)
                return

            return await func(message, state, *args, **kwargs)

        return wrapped

    return decorator
