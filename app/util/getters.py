from app import app
from app.models import Snippet, User
from hashids import Hashids
from .errors import SnippetNotFound, UserNotFound


def get_snippet_by_uuid(uuid):
    """Return a snippet by it's UUID (hashid) or raises a
    SnippetNotFound exception that renders 404"""
    hashid = Hashids(salt=app.config['HASHID_SALT'],
                     min_length=app.config['HASHID_LEN'])
    # If snippet doesn't exist, SnippetNotFound will 404
    try:
        decoded_id = hashid.decode(uuid)[0]
        snippet = Snippet.query.get(decoded_id)
    except:
        raise SnippetNotFound

    return snippet


def get_user_by_username(username):
    """Returns a use by it's email address or raises
    a UserNotFound exception that renders 404"""
    try:
        user = User.query.filter_by(username=username).one()
    except:
        raise UserNotFound

    return user
