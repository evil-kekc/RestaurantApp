import os

from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, Boolean, DateTime, func, \
    CheckConstraint
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.orm import relationship

from settings import BASE_DIR

if not os.path.exists(f'{BASE_DIR}/db_files'):
    os.makedirs(f'{BASE_DIR}/db_files')

engine_path = fr'{BASE_DIR}/db_files/bot_db.db'
engine = create_engine(f'sqlite:///{engine_path}')

Base = declarative_base()


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


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    order_time = Column(DateTime(timezone=True))
    is_cancelled = Column(Boolean, default=False)
    product = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    user = relationship('User', back_populates='orders')


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


if __name__ == '__main__':
    if not os.path.exists(f'{BASE_DIR}/db_files/bot_db.db'):
        Base.metadata.create_all(bind=engine)
        with Session(autoflush=True, bind=engine) as session:
            user1 = User(name="John", address="123 Street", phone_number="555-1234", is_admin=False)
            user2 = User(name="Alice", address="456 Avenue", phone_number="555-5678", is_admin=True)

            session.add_all([user1, user2])
            session.commit()

            product1 = Product(name="Pizza", price=10.99, is_available=True)
            product2 = Product(name="Burger", price=5.99, is_available=True)
            product3 = Product(name="Salad", price=7.99, is_available=False)

            session.add_all([product1, product2, product3])
            session.commit()

            order1 = Order(user_id=user1.id, product=product1.id, is_cancelled=False)
            order2 = Order(user_id=user2.id, product=product1.id, is_cancelled=True)

            session.add_all([order1, order2])
            session.commit()

            comment1 = Comment(user_id=user1.id, product_id=product1.id, comment_text="Great pizza!")
            comment2 = Comment(user_id=user2.id, product_id=product2.id, comment_text="Delicious burger!")

            session.add_all([comment1, comment2])
            session.commit()

            rating1 = Rating(user_id=user1.id, product_id=product1.id, rating_value=5)
            rating2 = Rating(user_id=user2.id, product_id=product2.id, rating_value=4)

            session.add_all([rating1, rating2])
            session.commit()

            admin1 = Admin(user_id=user1.id, admin_level=1)
            admin2 = Admin(user_id=user2.id, admin_level=2)

            session.add_all([admin1, admin2])
            session.commit()
    else:
        print('Database already exists')
