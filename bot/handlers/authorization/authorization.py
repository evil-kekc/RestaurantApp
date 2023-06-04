from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from config.bot_config import bot, get_start_kb_not_authorized, get_start_kb_authorized
from database.db_middleware import check_user_by_name_and_password, check_user_by_tg_id, set_tg_id
from static_buttons import CANCEL_BUTTON


class AuthorizationStates(StatesGroup):
    get_username = State()
    get_password = State()


async def start_authorization(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    if check_user_by_tg_id(tg_id=callback_query.from_user.id):
        keyboard = get_start_kb_authorized()
        await bot.send_message(callback_query.from_user.id,
                               'Привет, я бот, который поможет тебе сделать заказ из твоего любимого ресторана',
                               reply_markup=keyboard)

        await state.finish()

    await bot.send_message(callback_query.from_user.id, 'Введите имя пользователя', reply_markup=CANCEL_BUTTON)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await state.set_state(AuthorizationStates.get_username.state)


async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer('Введите пароль', reply_markup=CANCEL_BUTTON)
    await state.set_state(AuthorizationStates.get_password.state)


async def get_password(message: types.Message, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message_id)

    data = await state.get_data()
    username = data.get('username')
    password = message.text

    if check_user_by_name_and_password(name=username, password=password):
        set_tg_id(username=username, tg_id=message.from_user.id)
        keyboard = get_start_kb_authorized()
        await bot.send_message(message.from_user.id,
                               'Привет, я бот, который поможет тебе сделать заказ из твоего любимого ресторана',
                               reply_markup=keyboard)

        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await state.finish()
    else:
        keyboard = get_start_kb_not_authorized()
        await bot.send_message(message.from_user.id,
                               'Здравствуйте, для использования бота необходимо зарегистрироваться',
                               reply_markup=keyboard)

        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await state.finish()


def register_handlers_authorization(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_callback_query_handler(start_authorization, text='authorization')
    dp.register_message_handler(get_username, state=AuthorizationStates.get_username)
    dp.register_message_handler(get_password, state=AuthorizationStates.get_password)
