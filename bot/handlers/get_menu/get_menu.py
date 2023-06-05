from aiogram import types, Dispatcher
from aiogram.utils.callback_data import CallbackData

from config.bot_config import bot, create_inline_keyboard
from database.db_middleware import get_all_values, \
    get_photo_by_id
from database.models import Product

new_order_callback = CallbackData('new_order_callback', 'product_id', 'price')


async def get_menu(callback_query: types.CallbackQuery):
    await callback_query.answer()
    products = get_all_values(Product)
    for product in products:
        if product.is_available:
            buttons = {
                'Заказать': new_order_callback.new(product_id=product.id, price=product.price),
            }
            keyboard = create_inline_keyboard(**buttons)
            with open(get_photo_by_id(product.id), 'rb') as photo:
                await bot.send_photo(callback_query.from_user.id, photo=photo,
                                     caption=f'Блюдо: {product.name}\n'
                                             f'Цена: {product.price} руб.\n',
                                     reply_markup=keyboard)


def register_handlers_menu(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_callback_query_handler(get_menu, text='view_menu')
