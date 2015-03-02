from flask import render_template, redirect, url_for
from app import app, db
from app.forms import SnippetForm
from app.models import Snippet
from hashids import Hashids

hashids = Hashids(salt="I love 3 women")


@app.route('/', methods=['GET', 'POST'])
def index():
    snippet_form = SnippetForm()
    if snippet_form.validate_on_submit():
        s = Snippet(snippet_form.title.data, snippet_form.snippet.data)
        db.session.add(s)
        db.session.commit()
        uuid  = s.get_uuid()
        return redirect(url_for('show_snippet', snippet_id=uuid))
    return render_template('index.html', form=snippet_form)


@app.route('/<path:snippet_id>/')
def show_snippet(snippet_id):
    print(snippet_id)
    decoded_id = hashids.decode(snippet_id)[0]
    snippet = Snippet.query.get(decoded_id)
    return render_template('snippet.html', snippet=snippet) 

@app.route('/<snippet_id>/r')
def raw_snippet(snippet_id):
    decoded_id = hashids.decode(snippet_id)[0]
    snippet = Snippet.query.get(decoded_id)
    return render_template('raw.html', snippet=snippet)
