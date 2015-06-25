from app import app, db, login_manager
from app.forms import LoginForm, RequestResetForm
from app.forms import ChangePasswordForm, PasswordResetForm, SignupForm
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.util.email import generateToken, decodeToken, sendEmail
from app.util.getters import getUserByUsername
from app.util.decorators import anonymous_required
from app.models import Snippet, User
from flask_login import current_user, login_required, logout_user, login_user

user = Blueprint('user', __name__)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@user.route('/u/<path:username>/')
def snippets(username):
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
    return render_template('user/index.html', user=user, snippets=snippets)


@user.route('/login/', methods=['POST', 'GET'])
@anonymous_required
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
            return redirect(url_for('snippets.index'))
        return redirect(url_for('user.login'))

    return render_template('user/login.html', form=login_form)


@user.route('/logout/')
@login_required
def logout():
    """Route logs a user out of the session"""
    logout_user()
    return redirect(url_for('snippets.index'))


@user.route('/signup/', methods=['POST', 'GET'])
@anonymous_required
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
        .format(url_for('user.confirm_email', confirm_token=confirm_token, _external=True))

        sendEmail.delay(email, 'Confirm snip.space Email Address', email_body)
        flash('Check your email for a confirmation link!', 'info')
        return redirect(url_for('user.login'))
    return render_template('user/signup.html', form=signup_form)


@user.route('/confirm/<path:confirm_token>/')
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
    return redirect(url_for('user.login'))


@user.route('/request-reset/', methods=['GET', 'POST'])
@anonymous_required
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
                    .format(url_for('user.reset_password', reset_token=reset_token, _external=True))
            sendEmail.delay(email, 'Password Reset for snip.space', email_body)
            message = """A link to reset your password has been 
                         sent to the email address <strong>{}</strong>. 
                         Check your email, and follow the provided link 
                         to continue.""".format(email)
            return render_template('message.html', title="Reset Email Sent", message=message)
        else:
            flash('Email not found in our records.', 'danger')
            return redirect(url_for('user.request_reset'))

    return render_template('user/request_reset.html', form=form)


@user.route('/reset/<path:reset_token>/', methods=['GET', 'POST'])
@anonymous_required
def reset_password(reset_token):
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
            return redirect(url_for('user.login'))
    return render_template('user/reset_password.html', form=form, reset_token=reset_token)
    