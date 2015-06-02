import unittest
from app import app, db, bcrypt
from app.models import *
from flask import current_app
from flask.ext.bcrypt import Bcrypt
from flask.ext.sqlalchemy import SQLAlchemy
from app.views import index

class SnipstrTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.init_app(current_app)
            db.metadata.create_all(db.engine)
            bcrypt.init_app(current_app)
            self.db = db
            self.app = app.test_client()

    def test_index_returns_200(self):
        response = self.app.post('/', data=dict(title="Boo", snippet="Booooooooo"),follow_redirects=True)
        self.assertEqual(response.status, "200 OK")
        assert "Boo" in response.data


if __name__ == '__main__':
    unittest.main()
