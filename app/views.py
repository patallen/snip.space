from flask import render_template, redirect, url_for, abort, Response, make_response, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from app.forms import SnippetForm, SignupForm, LoginForm, DeleteForm
from app.models import Snippet, User, Language
from hashids import Hashids
import sendgrid
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

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

def generateConfirmationToken(email):
    return serializer.dumps(email, salt=app.config['EMAIL_CONF_SALT'])

def decodeConfirmationToken(token):
    email = serializer.loads(
        token,
        salt = app.config['EMAIL_CONF_SALT'],
        max_age = app.config['CONFIRM_EMAIL_EXP']
    )
    return email

def populateSnippetForm(form, snippet=None):
    """Populate the snippet form's language choicefield
    with languages from the database."""
    languages = [(lang.id, lang.display_text) for lang in Language.query.all()]
    form.language.choices = languages
    if snippet:
        form.language.data = snippet.language_id
        form.title.data = snippet.title
        form.snippet.data = snippet.body


def sendEmail(to_email, subject, body):
    """Use sendgrid's api to send email from noreply@snip.space"""
    sg = sendgrid.SendGridClient(
        app.config['SENDGRID_API_USER'],
        app.config['SENDGRID_API_KEY']
    )
    message = sendgrid.Mail()
    message.add_to(to_email)
    message.set_from('noreply@snip.space')
    message.set_subject(subject)
    message.set_html(body)

    sg.send(message)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Route allows users to create a new snippet"""
    snippet_form = SnippetForm()
    populateSnippetForm(snippet_form)
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


@app.route('/<path:snippet_uuid>/edit/', methods=['GET', 'POST'])
@login_required
def edit_snippet(snippet_uuid):
    """Route allows a user to modify a snippet if
    he or she is the owner"""
    snippet = getSnippetByUuid(snippet_uuid)

    if current_user != snippet.user:
        return "You are not the owner of this snippet"

    snippet_form = SnippetForm()
    populateSnippetForm(snippet_form, snippet)
    
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
        email = signup_form.email.data
        u = User(signup_form.username.data, email,
                 signup_form.password.data)
        db.session.add(u)
        db.session.commit()
        confirm_token = generateConfirmationToken(email)
        email_body = 'Welcome to snip.space! <a href="{}">Click here</a> to confirm your email!'\
        .format(url_for('confirm_email', confirm_token=confirm_token, _external=True))

        sendEmail(email, 'Confirm snip.space Email Address', email_body)
        return redirect(url_for('login'))
    return render_template('signup.html', form=signup_form)


@app.route('/confirm/<path:confirm_token>/')
def confirm_email(confirm_token):
    try:
        email = decodeConfirmationToken(confirm_token)
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
            flash('Incorrect username or password') 
        elif not registered_user.is_confirmed():
            flash('You must confirm your email before logging in.')
        else:
            login_user(registered_user)
            return redirect(url_for('index'))
        return redirect('login')

    return render_template('login.html', form=login_form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
