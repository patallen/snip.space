from app import app, db
from app.models import Language, Snippet
from app.forms import SnippetForm, DeleteForm
from app.util.errors import Unauthorized
from app.util.helpers import populate_choice_field
from app.util.getters import get_snippet_by_uuid

from datetime import date, timedelta
from flask import Blueprint, render_template, redirect
from flask import url_for, request, Response, make_response
from flask_login import login_required, current_user


snippets = Blueprint('snippets', __name__)


@snippets.route('/', methods=['GET', 'POST'])
def index():
    """Route allows users to create a new snippet"""
    snippet_form = SnippetForm()
    populate_choice_field(snippet_form)
    if snippet_form.validate_on_submit():
        s = Snippet(snippet_form.snippet.data)
        if snippet_form.title.data:
            s.title = snippet_form.title.data
        s.language = Language.query.get(snippet_form.language.data)
        if not current_user.is_anonymous():
            s.user = current_user
            s.private = snippet_form.private.data
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('snippets.show_snippet',
                                snippet_uuid=s.get_uuid()))
    if current_user.is_authenticated() and current_user.default_language:
        snippet_form.language.default = current_user.default_language_id
        snippet_form.process()

    return render_template('snippets/compose.html', form=snippet_form)


@snippets.route('/<path:snippet_uuid>/')
def show_snippet(snippet_uuid):
    """Route shows a snippet given it's
    unique identifier - displayed in a read only
    codemirror textarea"""

    snippet = get_snippet_by_uuid(snippet_uuid)
    if snippet.is_private() and snippet.user != current_user:
        raise Unauthorized("This snippet is private.")
    snippet.hits = snippet.hits + 1
    db.session.add(snippet)
    db.session.commit()

    return render_template('snippets/view.html', snippet=snippet)


@snippets.route('/<path:snippet_uuid>/edit/', methods=['GET', 'POST'])
@login_required
def edit_snippet(snippet_uuid):
    """Route allows a user to modify a snippet if
    he or she is the owner"""

    snippet = get_snippet_by_uuid(snippet_uuid)

    if current_user != snippet.user:
        raise Unauthorized("You must be the creator or a snippet to edit it.")

    snippet_form = SnippetForm()
    populate_choice_field(snippet_form)

    if snippet_form.validate_on_submit():
        snippet.body = snippet_form.snippet.data
        if snippet_form.title.data:
            snippet.title = snippet_form.title.data
        snippet.language = Language.query.get(snippet_form.language.data)
        snippet.private = snippet_form.private.data
        db.session.add(snippet)
        db.session.commit()
        return redirect(url_for('snippets.show_snippet',
                                snippet_uuid=snippet.get_uuid()))

    snippet_form.title.default = snippet.title
    snippet_form.snippet.default = snippet.body
    snippet_form.language.default = snippet.language_id
    snippet_form.private.default = snippet.is_private()
    snippet_form.process()

    return render_template('snippets/compose.html',
                           form=snippet_form,
                           snippet=snippet)


@snippets.route('/<path:snippet_uuid>/r/')
def raw_snippet(snippet_uuid):
    """Route returns the raw text of a snippet
    in a blank page in the browser"""
    snippet = get_snippet_by_uuid(snippet_uuid)
    return Response(snippet.body, mimetype='text/plain')


@snippets.route('/<path:snippet_uuid>/d/')
def download_snippet(snippet_uuid):
    """Route returns a downloadable file containing
    the raw text of a snippet"""

    snippet = get_snippet_by_uuid(snippet_uuid)

    body = snippet.body
    ext = snippet.language.extension
    response = make_response(body)

    response.headers['Content-Disposition'] =\
        "attachment; filename={}{}".format(snippet_uuid, ext)
    return response


@snippets.route('/<path:snippet_uuid>/delete/', methods=['GET', 'POST'])
@login_required
def delete_snippet(snippet_uuid):
    """Route lets the owner of a snippet delete
    the snippet"""
    snippet = get_snippet_by_uuid(snippet_uuid)

    if current_user != snippet.user:
        message = "You are not authorized to edit this snippet."
        return render_template('errorpages/401.html', message=message), 401

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(snippet)
        db.session.commit()
        return redirect(url_for('user.snippets',
                                username=current_user.username))
    return render_template('snippets/delete.html', form=form, snippet=snippet)


@snippets.route('/popular/')
def popular_snippets():
    """Route shows popular snippets based on the
    timeframe in the querystring"""
    page = request.args.get('page', 1)
    t = request.args.get('t', 'week')

    # determine time frame based on querystring (t)
    if t == 'month':
        from_date = date.today() - timedelta(days=30)
    elif t == 'year':
        from_date = date.today() - timedelta(days=365)
    elif t == 'all':
        from_date = None
    else:
        from_date = date.today() - timedelta(weeks=1)

    snippets = Snippet.query.filter_by(private=False)
    if from_date:
        snippets = snippets.filter(Snippet.date_added > from_date)

    snippets = snippets.order_by(Snippet.hits.desc())\
                       .paginate(int(page),
                                 app.config['SNIPPETS_PER_PAGE'],
                                 False)
    return render_template('snippets/list.html',
                           snippets=snippets,
                           view='Popular')


@snippets.route('/recent/')
def recent_snippets():
    """Route shows recent public snippets in the
    last 5 days, ordered by date_added"""

    page = request.args.get('page', 1)

    # Get date 5 days ago to query back to
    from_date = date.today() - timedelta(days=10)
    snippets = Snippet.query.filter_by(private=False)\
                            .filter(Snippet.date_added > from_date)\
                            .order_by(Snippet.date_added.desc())
    snippets = snippets.paginate(int(page),
                                 app.config['SNIPPETS_PER_PAGE'],
                                 False)
    return render_template('snippets/list.html',
                           snippets=snippets,
                           view='Recent')

@snippets.route('/about/')
def about():
    """Route displays the static about page"""
    return render_template('public/about.html')
