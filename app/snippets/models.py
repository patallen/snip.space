from app import app, db
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

    parent_fork_id = db.Column(db.Integer, db.ForeignKey('snippet.id'))
    parent_fork = db.relationship('Snippet',
                                  backref=db.backref('forks', lazy='dynamic'),
                                  remote_side='Snippet.id')

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
