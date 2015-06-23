from functools import wraps
from flask_login import current_user
from flask import redirect, url_for


def anonymous_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated():
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
