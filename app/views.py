from flask import render_template, redirect, url_for, abort
from flask.ext.login import login_user, logout_user, current_user
from app import app, db, login_manager
from app.forms import SnippetForm, SignupForm, LoginForm
from app.models import Snippet, User, Language
from hashids import Hashids


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


def getSnippetByUuid(uuid):
    """Return a snippet by it's UUID (hashid)"""
    hashid = Hashids(salt='salt', min_length=5)
    # Abort 404 if not valid or not in DB
    try:
        decoded_id = hashid.decode(uuid)[0]
        return Snippet.query.get(decoded_id)
    except:
        abort(404)


@app.route('/', methods=['GET', 'POST'])
def index():
    snippet_form = SnippetForm()
    if snippet_form.validate_on_submit():
        s = Snippet(snippet_form.title.data, snippet_form.snippet.data)
        s.language = Language.query.get(snippet_form.language.data)
        if not current_user.is_anonymous():
            s.user = current_user
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('show_snippet', snippet_uuid=s.get_uuid()))
    return render_template('index.html', form=snippet_form)


@app.route('/<path:snippet_uuid>/')
def show_snippet(snippet_uuid):
    try:
        snippet = getSnippetByUuid(snippet_uuid)
    except:
        abort(404)

    if snippet is None:
        return "Snippet {} does not exist.".format(snippet_id)
    else:
        return render_template('snippet.html', snippet=snippet)

@app.route('/u/<path:username>/')
def user_page(username):
    try:
        user = User.query.filter(User.username==username).one()
    except:
        abort(404)
    return render_template('user.html', user=user)


@app.route('/<path:snippet_uuid>/r')
def raw_snippet(snippet_uuid):
    snippet = getSnippetByUuid(snippet_uuid)
    return '<pre>{}</pre>'.format(snippet.body)


@app.route('/signup/', methods=['POST', 'GET'])
def signup():
    signup_form = SignupForm()
    if signup_form.validate_on_submit():
        u = User(signup_form.username.data, signup_form.email.data,
                 signup_form.password.data)
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=signup_form)


@app.route('/login/', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        registered_user = User.query.filter_by(username=username).first()
        if registered_user and registered_user.validate_pass(password):
            login_user(registered_user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login')) 

    return render_template('login.html', form=login_form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))
