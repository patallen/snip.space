from app import db, app
from sqlalchemy.ext.hybrid import hybrid_property
from app import bcrypt
import datetime
from hashids import Hashids


class Snippet(db.Model):
    __tablename__ = 'snippet'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), default='Untitled')
    body = db.Column(db.Text(), nullable=False)
    private = db.Column(db.Boolean, default=False)
    hits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language_id = db.Column(db.String, db.ForeignKey('language.id'))
    language = db.relationship('Language')
    date_added = db.Column(db.DateTime)

    def __init__(self, body):
        self.body = body
        self.date_added = datetime.datetime.utcnow()

    def __repr__(self):
        return '{}: {}'.format(self.id, self.title)

    def get_uuid(self):
        hashid = Hashids(salt=app.config['HASHID_SALT'],
                         min_length=app.config['HASHID_LEN'])
        return hashid.encode(self.id)

    def is_private(self):
        return self.private


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


class Language(db.Model):
    __tablename__ = 'language'
    id = db.Column(db.String(32), primary_key=True)
    display_text = db.Column(db.String(64), nullable=False)
    extension = db.Column(db.String(32))

    def __init__(self, id, display_text, ext):
        self.id = id
        self.display_text = display_text
        self.extension = ext

    def __repr__(self):
        return self.display_text
