import hashlib
import os
import unittest
from pathlib import Path

from sqlalchemy.orm import Session

from database.db_middleware import add_user, add_product, add_rating, add_comment
from database.models import User, Product, Rating, Comment, Base, engine, engine_path


def encode_password(password: str) -> str:
    """Hashes the password for comparison

    :param password: password value
    :return: encrypted password
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class DatabaseTestCase(unittest.TestCase):
    temp_db_path = engine_path

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
        user = add_user('TestUser', 'Test Address', 'TestPassword', '123456789')
        self.session.add(user)
        self.session.commit()
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, 3)
        self.assertEqual(user.name, 'TestUser')
        self.assertEqual(user.address, 'Test Address')
        self.assertEqual(user.password, encode_password('TestPassword'))
        self.assertEqual(user.phone_number, '123456789')

    def test_add_product(self):
        product = add_product('TestProduct', 10.0)
        self.session.add(product)
        self.session.commit()
        self.assertIsInstance(product, Product)
        self.assertEqual(product.name, 'TestProduct')
        self.assertEqual(product.price, 10.0)

    def test_add_rating(self):
        user = add_user('TestUser', 'Test Address', 'TestPassword', '123456789')
        self.session.add(user)
        product = add_product('TestProduct', 10.0)
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
        product = add_product('TestProduct', 10.0)
        self.session.add(product)
        self.session.commit()
        comment = add_comment(user.id, product.id, 'Test Comment')
        self.session.add(comment)
        self.session.commit()
        self.assertIsInstance(comment, Comment)
        self.assertEqual(comment.comment_text, 'Test Comment')
        self.assertEqual(comment.user.name, 'TestUser')


if __name__ == '__main__':
    unittest.main()
