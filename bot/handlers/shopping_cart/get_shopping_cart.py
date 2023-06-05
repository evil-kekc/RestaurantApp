from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from config.bot_config import bot, create_inline_keyboard
from database.db_middleware import get_photo_by_id, get_user_id_by_tg_id, get_user_cart_by_id, cancel_order_by_id

cancel_order_callback = CallbackData('cancel_order_callback', 'order_id')


async def get_cart(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.answer()
    user_id = get_user_id_by_tg_id(callback_query.from_user.id)
    orders = get_user_cart_by_id(user_id)
    for order in orders:
        if not order.cancelled:
            with open(get_photo_by_id(order.photo_id), 'rb') as photo:
                buttons = {
                    'Отменить заказ': cancel_order_callback.new(order_id=order.order_id),
                }
                keyboard = create_inline_keyboard(**buttons)
                await bot.send_photo(callback_query.from_user.id, photo=photo,
                                     caption=f'Блюдо: {order.name}\n'
                                             f'Количество: {order.quantity} шт.\n'
                                             f'Стоимость заказа: {order.cash} руб.',
                                     reply_markup=keyboard)


async def cancel_order(callback_query: types.CallbackQuery, callback_data: dict):
    order_id = int(callback_data.get('order_id'))
    cancelling = cancel_order_by_id(order_id=order_id)
    if cancelling:
        await callback_query.answer('Ваш заказ отменен', show_alert=True)
    else:
        await callback_query.answer('Что-то пошло не так :(', show_alert=True)
    message_id = callback_query.message.message_id
    await bot.delete_message(callback_query.from_user.id, message_id)


def register_handlers_cart(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_callback_query_handler(get_cart, text='view_cart')
    dp.register_callback_query_handler(cancel_order, cancel_order_callback.filter())
