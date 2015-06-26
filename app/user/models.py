from app import bcrypt, db
from sqlalchemy.ext.hybrid import hybrid_property
import datetime


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(60), unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    authenticated = db.Column(db.Boolean, default=True)
    active = db.Column(db.Boolean, default=True)
    join_date = db.Column(db.DateTime, nullable=False)
    snippets = db.relationship('Snippet', backref='user')
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_date = db.Column(db.DateTime)
    _password_hash = db.Column(db.String)
    default_language_id = db.Column(db.String, db.ForeignKey('language.id'))
    default_language = db.relationship('Language')

    def __init__(self, username, email, password):
        self.password = password.encode('utf-8')
        self.username = username
        self.email = email
        self.join_date = datetime.datetime.utcnow()

    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def _set_pass(self, password):
        self._password_hash = bcrypt.generate_password_hash(password)

    def validate_pass(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.authenticated

    def is_confirmed(self):
        return self.confirmed

    def get_id(self):
        return self.id

    def is_anonymous(self):
        return False

    def __repr__(self):
        return self.username
