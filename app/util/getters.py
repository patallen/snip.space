from app import app
from app.models import Snippet, User
from hashids import Hashids
from .errors import SnippetNotFound, UserNotFound
from flask import render_template

def getSnippetByUuid(uuid):
    """Return a snippet by it's UUID (hashid)"""
    hashid = Hashids(salt=app.config['HASHID_SALT'],
                     min_length=app.config['HASHID_LEN'])
    # If snippet doesn't exist, SnippetNotFound will 404
    try:
        decoded_id = hashid.decode(uuid)[0]
        snippet = Snippet.query.get(decoded_id)
    except:
        raise SnippetNotFound

    return snippet


def getUserByUsername(username):
    try:
        user = User.query.filter(User.username==username).one()
    except:
        raise UserNotFound

    return user