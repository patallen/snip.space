from app import db
import datetime

class Snippet(db.Model):
    __tablename__ = 'snippet'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text(), nullable=False)
    date_added = db.Column(db.DateTime)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.date_added = datetime.datetime.utcnow()
