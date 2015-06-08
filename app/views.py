from flask import render_template, redirect, url_for, abort, Response, make_response
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from app.forms import SnippetForm, SignupForm, LoginForm, DeleteForm
from app.models import Snippet, User, Language
from hashids import Hashids


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


def getSnippetByUuid(uuid):
    """Return a snippet by it's UUID (hashid)"""
    hashid = Hashids(salt=app.config['HASHID_SALT'],
                     min_length=app.config['HASHID_LEN'])
    # Abort 404 if not valid or not in DB
    try:
        decoded_id = hashid.decode(uuid)[0]
        snippet = Snippet.query.get(decoded_id)
    except:
        abort(404)
    return snippet 


@app.route('/', methods=['GET', 'POST'])
def index():
    """Route allows users to create a new snippet"""
    snippet_form = SnippetForm()
    if snippet_form.validate_on_submit():
        s = Snippet(snippet_form.snippet.data)
        if snippet_form.title.data:
            s.title = snippet_form.title.data
        s.language = Language.query.get(snippet_form.language.data)
        if not current_user.is_anonymous():
            s.user = current_user
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('show_snippet', snippet_uuid=s.get_uuid()))
    return render_template('index.html', form=snippet_form)


@app.route('/<path:snippet_uuid>/')
def show_snippet(snippet_uuid):
    """Route shows a snippet given it's 
    unique identifier - displayed in a read only
    codemirror textarea"""
    try:
        snippet = getSnippetByUuid(snippet_uuid)
        snippet.hits = snippet.hits + 1
        db.session.add(snippet)
        db.session.commit()
    except:
        return "Snippet does not exist."
    return render_template('snippet.html', snippet=snippet)


@app.route('/<path:snippet_uuid>/r/')
def raw_snippet(snippet_uuid):
    """Route returns the raw text of a snippet
    in a blank page in the browser"""
    snippet = getSnippetByUuid(snippet_uuid)
    return Response(snippet.body, mimetype='text/plain')

@app.route('/<path:snippet_uuid>/d/')
def download_snippet(snippet_uuid):
    """Route returns a downloadable file containing 
    the raw text of a snippet"""
    snippet = getSnippetByUuid(snippet_uuid).body
    response = make_response(snippet)
    response.headers['Content-Disposition'] = "attachment; filename={}.txt".format(snippet_uuid)
    return response


@app.route('/<path:snippet_uuid>/delete/', methods=['GET', 'POST'])
@login_required
def delete_snippet(snippet_uuid):
    """Route lets the owner of a snippet delete
    the snippet"""
    snippet = getSnippetByUuid(snippet_uuid)
    if not snippet:
        return "Snippet does not exist"

    if current_user != snippet.user:
       return "You do not have permission to delete that." 
    form = DeleteForm()
    
    if form.validate_on_submit():
        db.session.delete(snippet)
        db.session.commit()
        return redirect(url_for('user_page', username=current_user.username))
    return render_template('delete.html', form=form, snippet=snippet) 


@app.route('/u/<path:username>/')
def user_page(username):
    """Route returns snippets and their info for
    snippets created by specified user"""
    try:
        user = User.query.filter(User.username==username).one()
    except:
        abort(404)
    return render_template('user.html', user=user)


@app.route('/signup/', methods=['POST', 'GET'])
def signup():
    """Route for letting a user sign up"""
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
    """Route for logging in a user"""
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
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
