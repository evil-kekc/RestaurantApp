from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.utils.callback_data import CallbackData

from config.bot_config import bot, create_inline_keyboard, check_user_is_admin
from database.db_middleware import get_all_values, get_photo_by_id, change_product_is_available, get_name_by_id, \
    get_object_by_id, delete_product_by_id
from database.models import Product

stop_product = CallbackData('stop_product', 'product_id')
start_product = CallbackData('start_product', 'product_id')
delete_product = CallbackData('delete_product', 'product_id')


@check_user_is_admin()
async def start_edit(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.answer()

    products = get_all_values(Product)
    for product in products:
        if product.is_available:
            buttons = {
                'Поставить на стоп': stop_product.new(product_id=product.id),
                'Удалить продукт': delete_product.new(product_id=product.id),
            }
        else:
            buttons = {
                'Сделать активным': start_product.new(product_id=product.id),
                'Удалить продукт': delete_product.new(product_id=product.id),
            }

        keyboard = create_inline_keyboard(**buttons)

        with open(get_photo_by_id(product.id), 'rb') as photo:
            await bot.send_photo(callback_query.from_user.id, photo=photo,
                                 caption=f'Блюдо: {product.name}\n'
                                         f'Цена: {product.price} руб.\n',
                                 reply_markup=keyboard)


@check_user_is_admin()
async def stopping_product(callback_query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.finish()

    product_id = int(callback_data.get('product_id'))
    change_product_is_available(product_id=product_id, is_available=False)
    product = get_object_by_id(Product, product_id)

    await callback_query.answer(f'{product.name} поставлен на стоп', show_alert=True)

    message_id = callback_query.message.message_id
    await bot.delete_message(callback_query.from_user.id, message_id)

    buttons = {
        'Сделать активным': start_product.new(product_id=product.id),
        'Удалить продукт': delete_product.new(product_id=product.id),
    }
    keyboard = create_inline_keyboard(**buttons)

    with open(get_photo_by_id(product.id), 'rb') as photo:
        await bot.send_photo(callback_query.from_user.id, photo=photo,
                             caption=f'Блюдо: {product.name}\n'
                                     f'Цена: {product.price} руб.\n',
                             reply_markup=keyboard)


@check_user_is_admin()
async def starting_product(callback_query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.finish()

    product_id = int(callback_data.get('product_id'))
    change_product_is_available(product_id=product_id, is_available=True)
    product = get_object_by_id(Product, product_id)

    await callback_query.answer(f'{product.name} активен', show_alert=True)

    message_id = callback_query.message.message_id
    await bot.delete_message(callback_query.from_user.id, message_id)

    buttons = {
        'Поставить на стоп': stop_product.new(product_id=product.id),
        'Удалить продукт': delete_product.new(product_id=product.id),
    }
    keyboard = create_inline_keyboard(**buttons)

    with open(get_photo_by_id(product.id), 'rb') as photo:
        await bot.send_photo(callback_query.from_user.id, photo=photo,
                             caption=f'Блюдо: {product.name}\n'
                                     f'Цена: {product.price} руб.\n',
                             reply_markup=keyboard)


@check_user_is_admin()
async def deleting_product(callback_query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.finish()

    product_id = int(callback_data.get('product_id'))
    delete_product_by_id(Product, product_id)

    await callback_query.answer(f'Продукт удален', show_alert=True)

    message_id = callback_query.message.message_id
    await bot.delete_message(callback_query.from_user.id, message_id)


def register_handlers_edit_product(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_callback_query_handler(start_edit, text='edit_product')
    dp.register_callback_query_handler(stopping_product, stop_product.filter())
    dp.register_callback_query_handler(starting_product, start_product.filter())
    dp.register_callback_query_handler(deleting_product, delete_product.filter())
