from app import app
from flask import render_template


class SnippetNotFound(Exception):
    pass


class Unauthorized(Exception):
    pass


class UserNotFound(Exception):
    pass


@app.errorhandler(Unauthorized)
def unauthorized(e):
    """Custom errorhandler that renders a '401 Unauthorized' template"""
    message = "You are not authorized to edit this snippet."
    return render_template('errorpages/401.html', message=message), 401


@app.errorhandler(SnippetNotFound)
def snippet_not_found(e):
    """Custom errorhandler that renders a '404 snippet
    not found' template"""
    message = "The snippet you are looking for does not exist."
    return render_template('errorpages/404.html', message=message), 404


@app.errorhandler(UserNotFound)
def user_not_found(e):
    """Custom errorhandler that renders a '404 user
    not found' template"""
    message = "The user you are looking for does not exist."
    return render_template('errorpages/404.html', message=message), 404
