import hashlib
import logging
from datetime import datetime
from typing import Type, Generator, Union

from database.models import Session, Base, User, Product, Order, Comment, Rating, Admin, engine
from settings import setup_logger

logger = setup_logger('database')


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
             admin_level: int = 1) -> User | None:
    """Creates a new user in the database

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
            new_user = User(name=name, password=password_hash, address=address, phone_number=phone_number,
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


def add_product(name: str, price: Union[float, int], is_available: bool = False) -> Product | None:
    """Creates a product to the database

    :param is_available: product available for order or not
    :param name: product name
    :param price: product price
    :return: product object
    """
    with Session(autoflush=True, bind=engine) as session:
        try:
            new_product = Product(name=name, price=price, is_available=is_available)
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
