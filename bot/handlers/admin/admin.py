from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from config.bot_config import create_inline_keyboard, \
    check_user_is_admin


class AdminStates(StatesGroup):
    get_username = State()
    get_password = State()


@check_user_is_admin()
async def start_admin(message: types.Message, state: FSMContext):
    await state.finish()
    buttons = {
        'Добавить продукт': 'add_product',
        'Изменить продукт': 'edit_product',

    }
    keyboard = create_inline_keyboard(**buttons)
    await message.answer(f'Здравствуйте, {message.from_user.username}!\n'
                         f'Что хотите сделать?', reply_markup=keyboard)


def register_handlers_admin(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_message_handler(start_admin, commands='admin', state='*')
