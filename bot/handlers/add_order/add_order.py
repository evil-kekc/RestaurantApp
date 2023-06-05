import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from config.bot_config import bot, create_inline_keyboard
from database.db_middleware import get_user_id_by_tg_id, get_name_by_id, add_order
from database.models import Product
from handlers.get_menu.get_menu import new_order_callback

confirm_callback = CallbackData('confirm_callback', 'answer')


class OrderStates(StatesGroup):
    get_quantity = State()
    confirm = State()


async def start_ordering(callback_query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.finish()
    await callback_query.answer()

    product_id = callback_data.get('product_id')
    price = float(callback_data.get('price'))

    user_id = get_user_id_by_tg_id(callback_query.from_user.id)

    await state.update_data(product_id=product_id, user_id=user_id, price=price)

    await bot.send_message(callback_query.from_user.id, 'Введите количество товаров')
    await state.set_state(OrderStates.get_quantity.state)


async def get_quantity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = int(data.get('product_id'))
    quantity = message.text
    price = float(data.get('price'))
    try:
        quantity = int(message.text)
        if quantity < 0:
            await message.answer('Количество должно быть положительным числом')
            return
        await state.update_data(quantity=quantity)
    except ValueError:
        await message.answer('Проверьте правильность введенного количества')
        return

    buttons = {
        'Все верно': confirm_callback.new(answer='yes'),
        'Отмена': confirm_callback.new(answer='no'),
    }
    keyboard = create_inline_keyboard(**buttons)

    await message.answer(f'Проверьте правильность введенных данных:\n'
                         f'Наименование товара: {get_name_by_id(Product, product_id)}\n'
                         f'Количество: {quantity}\n'
                         f'Стоимость: {price * quantity} руб.',
                         reply_markup=keyboard)

    await state.set_state(OrderStates.confirm.state)


async def get_confirm(callback_query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    data = await state.get_data()
    product_id = int(data.get('product_id'))
    user_id = int(data.get('user_id'))
    quantity = int(data.get('quantity'))

    answer = callback_data.get('answer')
    if answer == 'yes':
        add_order(user=user_id, order_time=datetime.datetime.now(), product=product_id, quantity=quantity)
        await callback_query.answer('Заказ добавлен в корзину', show_alert=True)
    else:
        await callback_query.answer('Заказ отменен', show_alert=True)

    message_id = callback_query.message.message_id
    await bot.delete_message(callback_query.from_user.id, message_id)
    await state.finish()


def register_handlers_add_order(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_callback_query_handler(start_ordering, new_order_callback.filter(), state='*')
    dp.register_message_handler(get_quantity, state=OrderStates.get_quantity.state)
    dp.register_callback_query_handler(get_confirm, confirm_callback.filter(), state=OrderStates.confirm.state)
