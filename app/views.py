from flask import render_template, redirect, url_for
from flask.ext.login import login_user, logout_user, current_user
from app import app, db, login_manager
from app.forms import SnippetForm, SignupForm, LoginForm
from app.models import Snippet, User, Language


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/', methods=['GET', 'POST'])
def index():
    snippet_form = SnippetForm()
    if snippet_form.validate_on_submit():
        s = Snippet(snippet_form.title.data, snippet_form.snippet.data)
        s.language = Language.query.get(snippet_form.language.data)
        if not current_user.is_anonymous():
            s.user_id = current_user.id
        db.session.add(s)
        db.session.commit()
        snippet_id = s.id
        return redirect(url_for('show_snippet', snippet_id=snippet_id))
    return render_template('index.html', form=snippet_form)


@app.route('/<snippet_id>/')
def show_snippet(snippet_id):
    snippet = Snippet.query.get(snippet_id)

    if snippet is None:
        return "Snippet {} does not exist.".format(snippet_id)
    else:
        return render_template('snippet.html', snippet=snippet)


@app.route('/<snippet_id>/r')
def raw_snippet(snippet_id):
    snippet = Snippet.query.get(snippet_id)

    if snippet is None:
        return "Snippet {} does not exist.".format(snippet_id)
    else:
        return render_template('raw.html', snippet=snippet)


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
