from app import db
import datetime
from hashids import Hashids

hashids = Hashids(salt="I love 3 women")

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

    def get_uuid(self):
        hash_id = hashids.encode(self.id)
        return hash_id

