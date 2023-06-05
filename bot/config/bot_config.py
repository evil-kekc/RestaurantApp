import os
from functools import wraps

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from cachetools import TTLCache
from dotenv import load_dotenv

from database.db_middleware import check_user_by_tg_id, check_is_admin_by_tg_id
from settings import setup_logger

logger = setup_logger('bot')

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


def check_user_is_admin():
    """Checking if the user is admin

    :return:
    """

    def decorator(func):
        @wraps(func)
        async def wrapped(message: types.Message, state: FSMContext, *args, **kwargs):
            user_id = message.from_user.id

            if not check_is_admin_by_tg_id(tg_id=user_id):
                return

            return await func(message, state, *args, **kwargs)

        return wrapped

    return decorator


def get_start_kb_not_authorized() -> InlineKeyboardMarkup:
    """Getting the start keyboard object

    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.row(InlineKeyboardButton(
        'Регистрация',
        callback_data='registration'))
    keyboard.row(InlineKeyboardButton(
        'У меня уже есть аккаунт',
        callback_data='authorization'))
    return keyboard


def get_start_kb_authorized() -> InlineKeyboardMarkup:
    """Getting the start keyboard object

    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)

    keyboard.row(InlineKeyboardButton(
        'Посмотреть меню',
        callback_data='view_menu'))
    keyboard.row(InlineKeyboardButton(
        'Посмотреть корзину',
        callback_data='view_cart'))

    return keyboard


def create_keyboard(*args: str) -> ReplyKeyboardMarkup:
    """Creating Keyboard Buttons

    :param args: buttons
    :return: ReplyKeyboardMarkup object
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*args)
    return keyboard


def create_inline_keyboard(row_width: int = 1, **kwargs) -> InlineKeyboardMarkup:
    """Creating Inline Keyboard

    :param row_width: number of buttons per line
    :param kwargs: key - button text, value - button callback_data
    :return:
    """
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    for name, callback_data in kwargs.items():
        keyboard.add(InlineKeyboardButton(text=name, callback_data=callback_data))

    return keyboard


async def remove_keyboard(chat_id, message_id):
    """Keyboard removal

    :param chat_id: chat id
    :param message_id: message id
    :return:
    """
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
