from app import db
import datetime
from sqlalchemy.ext.hybrid import hybrid_property
import bcrypt


class Snippet(db.Model):
    __tablename__ = 'snippet'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_added = db.Column(db.DateTime)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.date_added = datetime.datetime.utcnow()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(60), unique=True)
    first_name = db.Column(db.String(30))
    _password_salt = db.Column(db.String)
    _password_hash = db.Column(db.String)

    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def _set_pass(self, password):
        self._password_salt = bcrypt.gensalt()
        self._password_hash = bcrypt.hashpw(password, self._password_salt)

    def validate_pass(self, password):
        return bcrypt.hashpw(password.encode('utf-8'),
                             self._password_hash) == self._password_hash

    def __init__(self, username, email, first_name, password):
        self.password = password.encode('utf-8')
        self.username = username
        self.email = email
        self.first_name = first_name
