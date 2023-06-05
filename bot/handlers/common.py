from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from config.bot_config import antispam, check_user_exists, get_start_kb_authorized


@antispam(rate=3, interval=5)
@check_user_exists()
async def cmd_start(message: types.Message, state: FSMContext):
    """Handling the start command

    :param message: message object
    :param state: state object
    :return:
    """
    await state.finish()
    keyboard = get_start_kb_authorized()

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
    dp.register_message_handler(cmd_cancel, Text(equals='отмена', ignore_case=True), state='*')
