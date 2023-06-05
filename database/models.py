import os

from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, Boolean, DateTime, func, \
    CheckConstraint, LargeBinary
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from settings import setup_logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(f'{BASE_DIR}/db_files'):
    os.makedirs(f'{BASE_DIR}/db_files')

engine_path = fr'{BASE_DIR}/db_files/bot_db.db'
engine = create_engine(f'sqlite:///{engine_path}')

Base = declarative_base()
logger = setup_logger('database')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    address = Column(String)
    phone_number = Column(String)
    is_admin = Column(Boolean, nullable=False, default=False)
    orders = relationship('Order', back_populates='user')
    comments = relationship('Comment', back_populates='user')
    ratings = relationship('Rating', back_populates='user')
    admin_level = relationship('Admin', back_populates='user')


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    price = Column(Float)
    is_available = Column(Boolean)
    image_data = Column(LargeBinary)
    orders = relationship('Order', back_populates='products')


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    order_time = Column(DateTime(timezone=True))
    is_cancelled = Column(Boolean, default=False)
    quantity = Column(Integer)
    user = relationship('User', back_populates='orders')
    product = Column(Integer, ForeignKey('products.id'))
    products = relationship('Product', back_populates='orders')


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    comment_text = Column(String)
    user = relationship('User', back_populates='comments')


class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    rating_value = Column(Integer, default=4)
    user = relationship('User', back_populates='ratings')


class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    admin_level = Column(Integer, CheckConstraint('admin_level BETWEEN 1 AND 2'))
    user = relationship('User', back_populates='admin_level')


class SettingsHistory(Base):
    __tablename__ = 'settings_history'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    settings_name = Column(String)
    old_value = Column(String)
    new_value = Column(String)
    change_time = Column(DateTime(timezone=True), onupdate=func.now())


class BackupHistory(Base):
    __tablename__ = 'backup_history'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    backup_time = Column(DateTime(timezone=True), onupdate=func.now())


Base.metadata.create_all(bind=engine)
