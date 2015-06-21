from app import app, db, login_manager
from app.forms import SnippetForm, SignupForm, LoginForm, DeleteForm, ChangePasswordForm, PreferencesForm, RequestResetForm, PasswordResetForm
from app.models import Snippet, User, Language
from datetime import datetime, date, timedelta
from flask import render_template, redirect, url_for, abort
from flask import Response, make_response, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from util.email import generateToken, decodeToken, sendEmail
from util.getters import getSnippetByUuid, getUserByUsername
from util.helpers import populateChoiceField
from util.errors import Unauthorized


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
            s.private = snippet_form.private.data
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('show_snippet', snippet_uuid=s.get_uuid()))
    if current_user.is_authenticated() and current_user.default_language:
        snippet_form.language.default = current_user.default_language_id
        snippet_form.process()

    return render_template('index.html', form=snippet_form)


@app.route('/<path:snippet_uuid>/')
def show_snippet(snippet_uuid):
    """Route shows a snippet given it's 
    unique identifier - displayed in a read only
    codemirror textarea"""
    
    snippet = getSnippetByUuid(snippet_uuid)
    if snippet.is_private() and snippet.user != current_user:
        raise Unauthorized("This snippet is private.")
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
        raise Unauthorized("You must be the creator or a snippet to edit it.")

    snippet_form = SnippetForm()
    populateChoiceField(snippet_form)
    
    if snippet_form.validate_on_submit():
        snippet.body = snippet_form.snippet.data
        if snippet_form.title.data:
            snippet.title = snippet_form.title.data
        snippet.language = Language.query.get(snippet_form.language.data)
        snippet.private = snippet_form.private.data
        db.session.add(snippet)
        db.session.commit()
        return redirect(url_for('show_snippet', snippet_uuid=snippet.get_uuid()))

    snippet_form.title.default = snippet.title
    snippet_form.snippet.default = snippet.body
    snippet_form.language.default = snippet.language_id
    snippet_form.private.default = snippet.is_private()
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
    return render_template('user.html', user=user, snippets=snippets)


@app.route('/settings/', methods=['GET', 'POST'])
@login_required
def user_settings():
    """Route for users to customize their settings"""
    prefs_form = PreferencesForm()
    populateChoiceField(prefs_form)
    if prefs_form.validate_on_submit():
        current_user.default_language = Language.query.get(prefs_form.language.data)
        db.session.add(current_user)
        db.session.commit()
        flash('Your preferences have been saved!', 'success')

    if current_user.default_language:
        prefs_form.language.default = current_user.default_language_id 
        prefs_form.process()
    
    return render_template('settings.html', prefs_form=prefs_form) 


@app.route('/changepass/', methods=['GET', 'POST'])
@login_required
def change_password():
    """Route for logged in users to change password"""
    pw_form = ChangePasswordForm()
    if pw_form.validate_on_submit():
        # If new password is not equal to old
        if not current_user.validate_pass(pw_form.newpw.data):
            current_user.password = pw_form.newpw.data
            flash('Password successfuly changed!', 'info')
            db.session.add(current_user)
            db.session.commit()
        else:
            flash('Password must differ from the old.', 'danger')

    return render_template('change_password.html', pw_form=pw_form) 


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

        sendEmail.delay(email, 'Confirm snip.space Email Address', email_body)
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
    flash('Your email has been confirmed! You man now log in.', 'success')
    return redirect(url_for('login'))


@app.route('/recent/')
def recent_snippets():
    """Route shows recent public snippets in the
    last 5 days, ordered by date_added"""
    page = 1
    if request.args.get('page'):
        page = request.args.get('page')
    
    # Get date 5 days ago to query back to
    from_date = date.today() - timedelta(days=5)
    snippets = Snippet.query.filter_by(private=False)\
                            .filter(Snippet.date_added > from_date)\
                            .order_by(Snippet.date_added.desc())
    snippets = snippets.paginate(int(page),
                                 app.config['SNIPPETS_PER_PAGE'],
                                 False)
    return render_template('recent_snippets.html', snippets=snippets)


@app.route('/request-reset/', methods=['GET', 'POST'])
def request_reset():
    form = RequestResetForm()

    if form.validate_on_submit():
        user = None
        try:
            user = User.query.filter(User.email == form.email.data).one()
        except:
            pass
        if user:
            email = user.email
            reset_token = generateToken(email) 
            email_body ='<a href="{}">Click here</a> to reset your snip.space password.'\
                    .format(url_for('reset_password', reset_token=reset_token, _external=True))
            sendEmail.delay(email, 'Password Reset for snip.space', email_body)
            message = """A link to reset your password has been 
                         sent to the email address <strong>{}</strong>. 
                         Check your email, and follow the provided link 
                         to continue.""".format(email)
            return render_template('message.html', title="Reset Email Sent", message=message)
        return redirect(url_for('request_reset'))

    return render_template('request_reset.html', form=form)


@app.route('/reset/<path:reset_token>/', methods=['GET', 'POST'])
def reset_password(reset_token):
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    try:
        email = decodeToken(reset_token)
    except SignatureExpired:
        return "This token has expired." 
    except BadSignature:
        return "Invalid token." 

    form = PasswordResetForm()

    if form.validate_on_submit():
        user = User.query.filter(User.email == email).one()
        if email != form.email.data:
            flash('Email not valid', 'danger')
        else:
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash('Your password has been reset. Log in!', 'success')
            return redirect(url_for('login'))
    return render_template('reset_password.html', form=form, reset_token=reset_token)            


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
