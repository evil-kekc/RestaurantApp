import hashlib
import os
import pathlib
import unittest
from pathlib import Path

from sqlalchemy.orm import Session

from database.db_middleware import add_user, add_product, add_rating, add_comment, set_tg_id, check_is_admin_by_tg_id, \
    change_product_is_available, get_object_by_id
from database.models import User, Product, Rating, Comment, Base, engine, engine_path


def encode_password(password: str) -> str:
    """Hashes the password for comparison

    :param password: password value
    :return: encrypted password
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class DatabaseTestCase(unittest.TestCase):
    temp_db_path = engine_path
    images_path = pathlib.Path(os.path.join(os.path.dirname(os.path.abspath(__file__))))
    photo_path = os.path.join(images_path, 'test_images', "test.jpg")

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.temp_db_path):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_db_path):
            os.remove(cls.temp_db_path)
            os.rmdir(Path(cls.temp_db_path).parent)

    def setUp(self):
        with Session(bind=engine) as session:
            self.session = session

    def tearDown(self):
        self.session.rollback()

    def test_add_user(self):
        user = add_user(name='TestUser', address='Test Address', password='TestPassword', phone_number='123456789',
                        tg_id=123456)
        self.session.add(user)
        self.session.commit()
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, 3)
        self.assertEqual(user.name, 'TestUser')
        self.assertEqual(user.address, 'Test Address')
        self.assertEqual(user.password, encode_password('TestPassword'))
        self.assertEqual(user.phone_number, '123456789')
        self.assertEqual(user.telegram_id, 123456)

    def test_add_product(self):
        product = add_product('TestProduct', 10.0, photo_path=self.photo_path)
        self.session.add(product)
        self.session.commit()
        self.assertIsInstance(product, Product)
        self.assertEqual(product.name, 'TestProduct')
        self.assertEqual(product.price, 10.0)

    def test_add_rating(self):
        user = add_user('TestUser', 'Test Address', 'TestPassword', '123456789')
        self.session.add(user)
        product = add_product('TestProduct', 10.0, photo_path=self.photo_path)
        self.session.add(product)
        self.session.commit()
        rating = add_rating(user.id, product.id, 5)
        self.session.add(rating)
        self.session.commit()
        self.assertIsInstance(rating, Rating)
        self.assertEqual(rating.rating_value, 5)
        self.assertEqual(rating.user.id, 2)
        self.assertEqual(rating.user.name, 'TestUser')

    def test_add_comment(self):
        user = add_user('TestUser', 'Test Address', 'TestPassword', '123456789')
        self.session.add(user)
        product = add_product('TestProduct', 10.0, photo_path=self.photo_path)
        self.session.add(product)
        self.session.commit()
        comment = add_comment(user.id, product.id, 'Test Comment')
        self.session.add(comment)
        self.session.commit()
        self.assertIsInstance(comment, Comment)
        self.assertEqual(comment.comment_text, 'Test Comment')
        self.assertEqual(comment.user.name, 'TestUser')

    def test_check_user_by_tg_id(self):
        user = add_user(name='TestUser', address='Test Address', password='TestPassword', phone_number='123456789',
                        tg_id=123456)
        self.session.add(user)
        self.assertEqual(user.telegram_id, 123456)

    def test_check_is_admin_by_tg_id(self):
        user = add_user(name='TestUser', address='Test Address', password='TestPassword', phone_number='123456789',
                        tg_id=1234567, is_admin=True)
        self.session.add(user)
        self.session.commit()
        result = check_is_admin_by_tg_id(user.telegram_id)
        self.assertEqual(result, True)

    def test_change_product_is_available(self):
        product = add_product('TestProduct1', 10.0, photo_path=self.photo_path, is_available=True)
        self.session.add(product)
        self.session.commit()
        change_product_is_available(product_id=product.id, is_available=False)
        self.session.commit()
        self.assertEqual(product.is_available, False)

    def test_get_object_by_id(self):
        product = add_product('TestProduct2', 10.0, photo_path=self.photo_path, is_available=True)
        self.session.add(product)
        self.session.commit()
        result = get_object_by_id(Product, product.id)
        self.assertIsInstance(result, Product)
        self.assertEqual(result.name, 'TestProduct2')


if __name__ == '__main__':
    unittest.main()
