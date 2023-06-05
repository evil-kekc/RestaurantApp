import os
import tempfile

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove

from config.bot_config import bot, check_user_is_admin
from config.static_buttons import CANCEL_BUTTON
from database.db_middleware import add_product


class AddProductStates(StatesGroup):
    get_name = State()
    get_price = State()
    get_photo = State()


@check_user_is_admin()
async def start_add(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.answer()

    await bot.send_message(callback_query.from_user.id, 'Введите название продукта', reply_markup=CANCEL_BUTTON)
    await state.set_state(AddProductStates.get_name.state)


@check_user_is_admin()
async def get_product_name(message: types.Message, state: FSMContext):
    await message.answer('Введите стоимость продукта', reply_markup=CANCEL_BUTTON)

    await state.update_data(product_name=message.text)
    await state.set_state(AddProductStates.get_price.state)


@check_user_is_admin()
async def get_product_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer('Введите стоимость в правильном формате, например: 10.99')
        return
    await state.update_data(price=price)
    await message.answer('Отправьте фото продукта', reply_markup=CANCEL_BUTTON)

    await state.set_state(AddProductStates.get_photo.state)


async def get_photo(message: types.Message, state: FSMContext):
    if message.photo:
        photo = message.photo[-1]

        data = await state.get_data()
        product_name = data.get('product_name')
        product_price = data.get('price')

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        await photo.download(destination=temp_file.name)
        photo_path = temp_file.name

        add_product(name=product_name, price=product_price, photo_path=photo_path, is_available=True)

        os.remove(photo_path)
        await message.answer('Продукт успешно добавлен', reply_markup=ReplyKeyboardRemove())

        await state.finish()


def register_handlers_add_product(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_callback_query_handler(start_add, text='add_product')
    dp.register_message_handler(get_product_name, state=AddProductStates.get_name)
    dp.register_message_handler(get_product_price, state=AddProductStates.get_price)
    dp.register_message_handler(get_photo, content_types=types.ContentType.PHOTO,
                                state=AddProductStates.get_photo)
