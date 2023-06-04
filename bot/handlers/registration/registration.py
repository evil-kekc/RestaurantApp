from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from config.bot_config import bot, ADMIN_ID, get_start_kb_authorized, get_start_kb_not_authorized
from database.db_middleware import add_user, check_user_by_tg_id
from static_buttons import CANCEL_BUTTON

callback_confirm = CallbackData('confirmation_expense', 'answer')


class RegistrationStates(StatesGroup):
    get_username = State()
    get_password = State()
    get_address = State()
    get_phone_number = State()
    confirm = State()


async def start_registration(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    if check_user_by_tg_id(tg_id=callback_query.from_user.id):
        await bot.send_message(callback_query.from_user.id, 'Вы уже зарегистрированы')
        await state.finish()
        return

    await bot.send_message(callback_query.from_user.id, 'Придумайте имя пользователя', reply_markup=CANCEL_BUTTON)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await state.set_state(RegistrationStates.get_username.state)


async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer('Придумайте пароль', reply_markup=CANCEL_BUTTON)
    await state.set_state(RegistrationStates.get_password.state)


async def get_password(message: types.Message, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message_id)
    await state.update_data(password=message.text)
    await message.answer('Введите адрес доставки', reply_markup=CANCEL_BUTTON)
    await state.set_state(RegistrationStates.get_address.state)


async def get_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer('Введите Ваш номер телефона', reply_markup=CANCEL_BUTTON)
    await state.set_state(RegistrationStates.get_phone_number.state)


async def confirmation(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.text)

    data = await state.get_data()
    username = data.get('username')
    password = data.get('password')
    address = data.get('address')
    phone_number = message.text

    keyboard = InlineKeyboardMarkup(row_width=5)
    keyboard.add(InlineKeyboardButton(text='Да', callback_data=callback_confirm.new(answer='Yes')))
    keyboard.add(InlineKeyboardButton(text='Нет', callback_data=callback_confirm.new(answer='No')))

    await message.answer(f'Всё верно?\n'
                         f'Имя пользователя: {username}\n'
                         f'Пароль: {password}\n'
                         f'Адрес: {address}\n'
                         f'Номер телефона: {phone_number}\n',
                         reply_markup=keyboard)
    await state.set_state(RegistrationStates.confirm.state)


async def confirm(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['answer'] == 'Yes':
        await callback_query.answer('Ваши данные успешно сохранены', show_alert=True)
        data = await state.get_data()
        username = data.get('username')
        password = data.get('password')
        address = data.get('address')
        phone_number = data.get('phone_number')

        if callback_query.from_user.id == ADMIN_ID:
            is_admin = True
        else:
            is_admin = False

        add_user(name=username, tg_id=callback_query.from_user.id, password=password, address=address,
                 phone_number=phone_number, is_admin=is_admin)

        keyboard = get_start_kb_authorized()
        await bot.send_message(callback_query.from_user.id,
                               'Привет, я бот, который поможет тебе сделать заказ из твоего любимого ресторана',
                               reply_markup=keyboard)

        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await state.finish()
    else:
        await callback_query.answer('Регистрация отменена', show_alert=True)
        keyboard = get_start_kb_not_authorized()
        await bot.send_message(callback_query.from_user.id,
                               'Здравствуйте, для использования бота необходимо зарегистрироваться',
                               reply_markup=keyboard)

        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await state.finish()


def register_handlers_registration(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_callback_query_handler(start_registration, text='registration')
    dp.register_message_handler(get_username, state=RegistrationStates.get_username)
    dp.register_message_handler(get_password, state=RegistrationStates.get_password)
    dp.register_message_handler(get_address, state=RegistrationStates.get_address)
    dp.register_message_handler(confirmation, state=RegistrationStates.get_phone_number)
    dp.register_callback_query_handler(confirm, callback_confirm.filter(), state=RegistrationStates.confirm)
