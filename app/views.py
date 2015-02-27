from flask import render_template, redirect, url_for
from app import app, db
from app.forms import SnippetForm
from app.models import Snippet


@app.route('/', methods=['GET', 'POST'])
def index():
    snippet_form = SnippetForm()
    if snippet_form.validate_on_submit():
        s = Snippet(snippet_form.title.data, snippet_form.snippet.data)
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('show_snippet', snippet_id=s.id))
    return render_template('index.html', form=snippet_form)


@app.route('/<snippet_id>')
def show_snippet(snippet_id):
    snippet = Snippet.query.get(snippet_id)
    return render_template('snippet.html', snippet=snippet)

