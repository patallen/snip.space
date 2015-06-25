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
from util.decorators import anonymous_required


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


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


@app.route('/request-reset/', methods=['GET', 'POST'])
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
                    .format(url_for('reset_password', reset_token=reset_token, _external=True))
            sendEmail.delay(email, 'Password Reset for snip.space', email_body)
            message = """A link to reset your password has been 
                         sent to the email address <strong>{}</strong>. 
                         Check your email, and follow the provided link 
                         to continue.""".format(email)
            return render_template('message.html', title="Reset Email Sent", message=message)
        else:
            flash('Email not found in our records.', 'danger')
            return redirect(url_for('request_reset'))

    return render_template('request_reset.html', form=form)


@app.route('/reset/<path:reset_token>/', methods=['GET', 'POST'])
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
            return redirect(url_for('login'))
    return render_template('reset_password.html', form=form, reset_token=reset_token)            


@app.route('/login/', methods=['POST', 'GET'])
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
            return redirect(url_for('index'))
        return redirect('login')

    return render_template('login.html', form=login_form)


@app.route('/logout/')
@login_required
def logout():
    """Route logs a user out of the session"""
    logout_user()
    return redirect(url_for('index'))
