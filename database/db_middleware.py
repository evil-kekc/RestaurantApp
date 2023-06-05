import base64
import hashlib
import logging
import tempfile
from datetime import datetime
from typing import Type, Generator, Union, Iterable, NamedTuple

from sqlalchemy.orm import Session

from database.models import Base, User, Product, Order, Comment, Rating, Admin, engine
from settings import setup_logger

logger = setup_logger('database')


class Cart(NamedTuple):
    name: str
    quantity: int
    cash: float
    cancelled: bool
    photo_id: int
    order_id: int


def get_all_values(cls: Type[Base]) -> Generator:
    """Getting all values from a table in a database

    :param cls: table object
    :return: database element generator object
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            objects = session.query(cls).all()
            for obj in objects:
                yield obj
        except Exception as ex:
            logger.error(repr(ex))
            return


def get_name_by_id(cls: Type[Base], id_: int):
    """Getting name from the database by id

    :param id_: id value
    :param cls: table object
    :return: database element generator object
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            obj = session.query(cls).filter(cls.id == id_).first()
            if obj:
                return obj.name
            else:
                logging.warning(f'Object from id:<{id_}> not found in table <{cls.__name__}>')
                return
        except Exception as ex:
            logger.error(repr(ex))
            return


def get_id_by_name(cls: Type[Base], name: str):
    """Getting id from the database by name

    :param cls: table object
    :param name: name value
    :return:
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            obj = session.query(cls).filter(cls.name == name).first()
            if obj:
                return obj.id
            else:
                logging.warning(f'Object name:<{name}> not found in table <{cls.__name__}>')
        except Exception as ex:
            logger.error(repr(ex))
            return


def add_user(name: str, address: str, password: str, phone_number: str, is_admin: bool = None,
             admin_level: int = 1, tg_id: int = None) -> User | None:
    """Creates a new user in the database

    :param tg_id: telegram id
    :param password: user password
    :param admin_level: admin level
    :param name: username
    :param address: user address
    :param phone_number: user phone number
    :param is_admin: boolean admin
    :return: user object
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if tg_id:
                new_user = User(telegram_id=tg_id, name=name, password=password_hash, address=address,
                                phone_number=phone_number,
                                is_admin=is_admin)
            else:
                new_user = User(name=name, password=password_hash, address=address,
                                phone_number=phone_number,
                                is_admin=is_admin)
            session.add(new_user)
            session.commit()
            if is_admin and admin_level is not None:
                admin = Admin(user_id=new_user.id, admin_level=admin_level)
                session.add(admin)
                session.commit()
            return new_user
        except Exception as ex:
            logger.error(repr(ex))
            return


def add_product(name: str, price: Union[float, int], photo_path: str, is_available: bool = False) -> Product | None:
    """Creates a product in the database

    :param is_available: product available for order or not
    :param name: product name
    :param price: product price
    :param photo_path: photo path
    :return: product object
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            with open(fr'{photo_path}', 'rb') as file:
                image_data = file.read()

            new_product = Product(name=name, price=price, is_available=is_available, image_data=image_data)
            session.add(new_product)
            session.commit()

            return new_product
        except Exception as ex:
            logger.error(repr(ex))
            return


async def add_product_from_tg(name: str, price: float, photo: bytes, is_available: bool = False) -> Product | None:
    """Creates a product in the database

    :param is_available: product available for order or not
    :param name: product name
    :param price: product price
    :param photo: photo bytes
    :return: product object
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            encoded_photo = base64.b64encode(photo).decode('utf-8')  # Кодируем фото в формате base64

            new_product = Product(name=name, price=price, is_available=is_available, image_data=encoded_photo)
            session.add(new_product)
            session.commit()

            return new_product
        except Exception as ex:
            logger.error(repr(ex))
            return


def add_rating(user: Union[int, str], product: Union[int, str], rating_value: int = None) -> Rating | None:
    """Creates a rating for a product to the database

    :param user: username or user id
    :param product: product name or product id
    :param rating_value: rating value
    :return:
    """
    try:
        with Session(autoflush=True, bind=engine) as session:
            if type(user) is str:
                user = get_id_by_name(User, user)
                if not user:
                    logging.warning(f'User <{user}> does not exists')
                    return
            if type(product) is str:
                product = get_id_by_name(Product, product)
                if not product:
                    logging.warning(f'Product <{product}> does not exists')
                    return

            new_rating = Rating(user_id=user, product_id=product, rating_value=rating_value)
            session.add(new_rating)
            session.commit()
            return new_rating
    except Exception as ex:
        logger.error(repr(ex))
        return


def add_comment(user: Union[int, str], product: Union[int, str], comment_text: str) -> Comment | None:
    """Creates new comment for a product to the database

    :param user: username or user id
    :param product: product name or product id
    :param comment_text: comment text
    :return:
    """
    try:
        with Session(autoflush=True, bind=engine) as session:
            if type(user) is str:
                user = get_id_by_name(User, user)
                if not user:
                    logging.warning(f'User <{user}> does not exists')
                    return
            if type(product) is str:
                product = get_id_by_name(Product, product)
                if not product:
                    logging.warning(f'Product <{product}> does not exists')
                    return

            new_comment = Comment(user_id=user, product_id=product, comment_text=comment_text)
            session.add(new_comment)
            session.commit()
            return new_comment
    except Exception as ex:
        logger.error(repr(ex))
        return


def add_order(user: Union[int, str], order_time: datetime, product: Union[int, str], quantity: int = 1,
              is_cancelled: bool = False) -> Order | None:
    """Adding an order to the database

    :param product: id or product name
    :param user: username or user id
    :param order_time: order time
    :param quantity: quantity
    :param is_cancelled: canceled order or not
    :return:
    """
    try:
        with Session(autoflush=True, bind=engine) as session:
            if type(user) is str:
                user = get_id_by_name(User, user)
                if not user:
                    logging.warning(f'User <{user}> does not exists')
                    return

            if type(product) is str:
                product = get_id_by_name(Product, product)
                if not product:
                    logging.warning(f'Product <{product}> does not exists')
                    return

            new_order = Order(user_id=user, order_time=order_time, is_cancelled=is_cancelled, product=product,
                              quantity=quantity)
            session.add(new_order)
            session.commit()
            return new_order
    except Exception as ex:
        logger.error(repr(ex))
        return


def check_user_by_name_and_password(name: str, password: str) -> bool | None:
    """Checks for the existence of a user by name and password

    :param name: username
    :param password: user password
    :return:
    """
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    with Session(autoflush=True, bind=engine) as session:
        try:
            user = session.query(User).filter_by(name=name, password=password_hash).first()
            if user:
                return True
            else:
                logger.warning(f'User <{name}> <{password}> not found')
                return
        except Exception as ex:
            logger.error(repr(ex))


def check_user_by_tg_id(tg_id: int) -> bool | None:
    """User Telegram id check

    :param tg_id: user Telegram id
    :return: True if exists and None if not exists
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            user = session.query(User).filter_by(telegram_id=tg_id).first()
            if user:
                return True
            else:
                logger.warning(f'User telegram_id:<{tg_id}> not found')
                return
        except Exception as ex:
            logger.error(repr(ex))
            return


def set_tg_id(tg_id: int, username: str) -> Type[User] | None:
    """Установка Telegram id в поле id пользователя

    :param tg_id: Telegram id
    :param username: username
    :return: User object or None if user not found
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            user = session.query(User).filter_by(name=username).first()
            if user:
                user.telegram_id = tg_id
                session.commit()
                return user
            else:
                logger.warning(f'User telegram_id:<{tg_id}> not found')
                return
        except Exception as ex:
            logger.error(repr(ex))
            return


def get_photo_by_id(product_id: int) -> str | None:
    """Getting a photo by id

    :param product_id: product id
    :return: Path
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                image_data = product.image_data
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_file.write(image_data)

                    photo_path = temp_file.name

                return photo_path
            else:
                logger.warning(f'Image image_id:<{product.id}> not found')
                return
        except Exception as ex:
            logger.error(repr(ex))
            return


def check_is_admin_by_tg_id(tg_id: id) -> bool | None:
    """Checking if a user is an admin by his Telegram id

    :param tg_id: Telegram id
    :return: True if user is admin
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            user = session.query(User).filter(User.telegram_id == tg_id).first()
            if user.is_admin:
                return True
        except Exception as ex:
            logger.error(repr(ex))
            return


def change_product_is_available(product_id: int, is_available: bool) -> Type[Product] | None:
    """Product state change

    :param is_available: True or False
    :param product_id: product_id
    :return:
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            if product:
                product.is_available = is_available
                session.commit()
                return product
            else:
                logger.warning(f'Product id:<{product_id}> not found')
                return
        except Exception as ex:
            logger.error(repr(ex))
            return


def get_object_by_id(cls: Type[Base], id_: int):
    """Getting object from the database by id

    :param id_: id value
    :param cls: table object
    :return: database element object
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            obj = session.query(cls).filter(cls.id == id_).first()
            if obj:
                return obj
            else:
                logging.warning(f'Object from id:<{id_}> not found in table <{cls.__name__}>')
                return
        except Exception as ex:
            logger.error(repr(ex))
            return


def delete_product_by_id(cls: Type[Base], id_: int):
    """Delete object from the database by id

    :param cls: table object
    :param id_: id value
    :return:
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            obj = session.query(cls).filter(cls.id == id_).first()
            if obj:
                session.delete(obj)
                session.commit()
            else:
                logging.warning(f'Object from id:<{id_}> not found in table <{cls.__name__}>')
                return
        except Exception as ex:
            logger.error(repr(ex))
            return


def get_user_id_by_tg_id(tg_id: int) -> int | None:
    """Getting user_id from the database by Telegram id

    :param tg_id: Telegram id
    :return: user id
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            user = session.query(User).filter(User.telegram_id == tg_id).first()
            if user:
                return user.id
            else:
                logging.warning(f'User from telegram_id:<{tg_id}> not found>')
                return
        except Exception as ex:
            logger.error(repr(ex))
            return


def get_user_cart_by_id(user_id: int) -> Iterable | None:
    """Receiving user orders

    :param user_id: user_id
    :return: Order
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                orders = user.orders
                for order in orders:
                    products = session.query(Product).filter(Product.orders.any(Order.id == order.id)).all()
                    for product in products:
                        cash = product.price * order.quantity
                        yield Cart(name=product.name, quantity=order.quantity, cash=cash, cancelled=order.is_cancelled,
                                   photo_id=product.id, order_id=order.id)
            else:
                logging.warning(f'User from id:<{user_id}> not found>')
                return
        except Exception as ex:
            logger.error(repr(ex))
            return


def cancel_order_by_id(order_id: int) -> bool | None:
    """Cancellations

    :param order_id: order id
    :return:
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            order = session.query(Order).filter_by(id=order_id).first()
            if order:
                order.is_cancelled = True
                session.commit()
                return True
            else:
                logging.warning(f'Order from id:<{order_id}> not found>')
                return
        except Exception as ex:
            logger.error(repr(ex))
            return
