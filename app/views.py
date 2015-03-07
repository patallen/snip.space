from flask import render_template, redirect, url_for
from app import app, db
from app.forms import SnippetForm, SignupForm
from app.models import Snippet, User


@app.route('/', methods=['GET', 'POST'])
def index():
    snippet_form = SnippetForm()
    if snippet_form.validate_on_submit():
        s = Snippet(snippet_form.title.data, snippet_form.snippet.data)
        db.session.add(s)
        db.session.commit()
        snippet_id = s.id
        return redirect(url_for('show_snippet', snippet_id=snippet_id))
    return render_template('index.html', form=snippet_form)


@app.route('/<path:snippet_id>/')
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
                 signup_form.first_name.data, signup_form.password.data)
        db.session.add(u)
        db.session.commit()
        return redirect('/')
    return render_template('signup.html', form=signup_form)
