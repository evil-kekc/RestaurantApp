from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config.bot_config import antispam, check_user_exists


@antispam(rate=3, interval=5)
@check_user_exists()
async def cmd_start(message: types.Message, state: FSMContext):
    """Handling the start command

    :param message: message object
    :param state: state object
    :return:
    """
    await state.finish()
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.row(InlineKeyboardButton(
        'Оформить заказ',
        callback_data='new_order'))
    keyboard.row(InlineKeyboardButton(
        'Посмотреть корзину',
        callback_data='view_cart'))

    await message.answer('Привет, я бот, который поможет тебе сделать заказ из твоего любимого ресторана',
                         reply_markup=keyboard)


@antispam(rate=3, interval=5)
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Handling the cancel command

    :param message: message object
    :param state: state object
    :return:
    """
    await state.finish()
    await message.answer('Действие отменено', reply_markup=types.ReplyKeyboardRemove())


def register_handlers_common(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_message_handler(cmd_start, commands='start', state='*')
    dp.register_message_handler(cmd_cancel, commands='cancel', state='*')
    dp.register_message_handler(cmd_start, Text(equals='отмена', ignore_case=True), state='*')
