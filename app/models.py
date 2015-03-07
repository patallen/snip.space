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

    def __repr__(self):
        return '<ID: {}>'.format(self.id)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(60), unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    authenticated = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    join_date = db.Column(db.DateTime, nullable=False)
    _password_hash = db.Column(db.String)

    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def _set_pass(self, password):
        password_salt = bcrypt.gensalt()
        self._password_hash = bcrypt.hashpw(password, password_salt)

    def validate_pass(self, password):
        return bcrypt.hashpw(password.encode('utf-8'),
                             self._password_hash) == self._password_hash

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.authenticated

    def __init__(self, username, email, password):
        self.password = password.encode('utf-8')
        self.username = username
        self.email = email
        self.join_date = datetime.datetime.utcnow()
