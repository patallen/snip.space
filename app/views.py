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


            
