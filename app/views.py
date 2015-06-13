from app import app, db, login_manager
from app.forms import SnippetForm, SignupForm, LoginForm, DeleteForm
from app.models import Snippet, User, Language
from datetime import datetime
from flask import render_template, redirect, url_for, abort, Response, make_response, flash
from flask_login import login_user, logout_user, current_user, login_required
from util.email import generateToken, decodeToken, sendEmail
from util.getters import getSnippetByUuid, getUserByUsername
from util.helpers import populateChoiceField


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/', methods=['GET', 'POST'])
def index():
    """Route allows users to create a new snippet"""
    snippet_form = SnippetForm()
    populateChoiceField(snippet_form)
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
    
    snippet = getSnippetByUuid(snippet_uuid)
    snippet.hits = snippet.hits + 1
    db.session.add(snippet)
    db.session.commit()

    return render_template('snippet.html', snippet=snippet)


@app.route('/<path:snippet_uuid>/edit/', methods=['GET', 'POST'])
@login_required
def edit_snippet(snippet_uuid):
    """Route allows a user to modify a snippet if
    he or she is the owner"""

    snippet = getSnippetByUuid(snippet_uuid)

    if current_user != snippet.user:
        message = "You are not authorized to edit this snippet."
        return render_template('errorpages/401.html', message=message), 401

    snippet_form = SnippetForm()
    populateChoiceField(snippet_form)
    
    if snippet_form.validate_on_submit():
        snippet.body = snippet_form.snippet.data
        if snippet_form.title.data:
            snippet.title = snippet_form.title.data
        snippet.language = Language.query.get(snippet_form.language.data)
        db.session.add(snippet)
        db.session.commit()
        return redirect(url_for('show_snippet', snippet_uuid=snippet.get_uuid()))

    snippet_form.title.default = snippet.title
    snippet_form.snippet.default = snippet.body
    snippet_form.language.default = snippet.language_id
    snippet_form.process()

    return render_template('index.html', form=snippet_form, snippet=snippet)   


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

    snippet = getSnippetByUuid(snippet_uuid)

    body = snippet.body
    ext = snippet.language.extension
    response = make_response(body)
    
    response.headers['Content-Disposition'] =\
                     "attachment; filename={}{}"\
                     .format(snippet_uuid, ext)
    return response


@app.route('/<path:snippet_uuid>/delete/', methods=['GET', 'POST'])
@login_required
def delete_snippet(snippet_uuid):
    """Route lets the owner of a snippet delete
    the snippet"""
    snippet = getSnippetByUuid(snippet_uuid)
 
    if current_user != snippet.user:
        message = "You are not authorized to edit this snippet."
        return render_template('errorpages/401.html', message=message), 401

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
    user = getUserByUsername(username)

    return render_template('user.html', user=user)


@app.route('/signup/', methods=['POST', 'GET'])
def signup():
    """Route for letting a user sign up"""
    signup_form = SignupForm()
    if signup_form.validate_on_submit():
        email = signup_form.email.data
        u = User(signup_form.username.data, email,
                 signup_form.password.data)
        db.session.add(u)
        db.session.commit()
        confirm_token = generateToken(email)
        email_body = 'Welcome to snip.space! <a href="{}">Click here</a> to confirm your email!'\
        .format(url_for('confirm_email', confirm_token=confirm_token, _external=True))

        sendEmail(email, 'Confirm snip.space Email Address', email_body)
        flash('Check your email for a confirmation link!', 'info')
        return redirect(url_for('login'))
    return render_template('signup.html', form=signup_form)


@app.route('/confirm/<path:confirm_token>/')
def confirm_email(confirm_token):
    """Route takes a token that is sent to users to confirm
    an email address. If email address exists in the database,
    the user's confirmed status is set to true."""
    try:
        email = decodeToken(confirm_token)
    except SignatureExpired:
        return "This token has expired." 
    except BadSignature:
        return "Invalid token." 

    user = User.query.filter(User.email == email).one()

    if user.is_confirmed():
        return "You have already confirmed your email address."
    user.confirmed = True
    user.confirmed_date = datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('login'))


@app.route('/login/', methods=['POST', 'GET'])
def login():
    """Log in users if they are registered and confirmed,
    provided they supply the correct password"""
    login_form = LoginForm()

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        registered_user = User.query.filter_by(username=username).first()

        if not registered_user or not registered_user.validate_pass(password):
            flash('Incorrect username or password', 'danger') 
        elif not registered_user.is_confirmed():
            flash('You must confirm your email before logging in.', 'danger')
        else:
            login_user(registered_user)
            return redirect(url_for('index'))
        return redirect('login')

    return render_template('login.html', form=login_form)


@app.route('/logout/')
@login_required
def logout():
    """Route logs a user out of the session"""
    logout_user()
    return redirect(url_for('index'))
