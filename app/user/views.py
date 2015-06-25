from app import app
from flask import Blueprint, request, render_template
from app.util.getters import getUserByUsername
from app.models import Snippet
from flask_login import current_user

user = Blueprint('user', __name__, url_prefix='/u')

@user.route('/<path:username>/')
def snippets(username):
    """Route returns snippets and their info for
    snippets created by specified user"""
    user = getUserByUsername(username)

    # set order_by variables based on querystring
    direction = request.args.get('dir', 'asc')
    field = request.args.get('sort', 'date')

    # set page to 1 in case it wasn't specified
    page = 1
    if request.args.get('page'):
        page = request.args.get('page')
   
    # set base query for user's snippets
    snipQuery = Snippet.query.filter(Snippet.user == user)
    if current_user != user:
        snipQuery = snipQuery.filter(Snippet.private == False)

    # ensure direction and field are valid
    if field not in ('date', 'title', 'views', 'syntax'):
        field = 'title'
    else:
        if field == 'date':
            field = 'date_added'
        if field == 'views':
            field = 'hits'
        if field == 'syntax':
            field = 'language_id'
    if direction not in ('desc', 'asc'):
        direction = 'asc'

    sort_by = '{} {}'.format(field, direction)
    snipQuery = snipQuery.order_by(sort_by)

    snippets = snipQuery.paginate(int(page), app.config['SNIPPETS_PER_PAGE'], False)
    return render_template('user/index.html', user=user, snippets=snippets)