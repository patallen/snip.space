from app import app
from flask import render_template


class SnippetNotFound(Exception):
    pass


class UserNotFound(Exception):
    pass


@app.errorhandler(SnippetNotFound)
def snippet_not_found(e):
    message = "The snippet you are looking for does not exist."
    return render_template('errorpages/404.html', message=message), 404


@app.errorhandler(UserNotFound)
def user_not_found(e):
    message = "The user you are looking for does not exist."
    return render_template('errorpages/404.html', message=message), 404