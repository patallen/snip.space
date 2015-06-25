from app import db
from app.forms import PreferencesForm, ChangePasswordForm
from app.models import Language
from app.util.helpers import populate_choice_field
from flask import flash, Blueprint, render_template
from flask_login import current_user, login_required

settings = Blueprint('settings', __name__)


@settings.route('/settings/', methods=['GET', 'POST'])
@login_required
def user_settings():
    """Route for users to customize their settings"""
    prefs_form = PreferencesForm()
    populate_choice_field(prefs_form)
    if prefs_form.validate_on_submit():
        current_user.default_language = Language.query.get(
            prefs_form.language.data
        )
        db.session.add(current_user)
        db.session.commit()
        flash('Your preferences have been saved!', 'success')

    if current_user.default_language:
        prefs_form.language.default = current_user.default_language_id
        prefs_form.process()

    return render_template('settings/settings.html', prefs_form=prefs_form)


@settings.route('/changepass/', methods=['GET', 'POST'])
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

    return render_template('settings/change_password.html', pw_form=pw_form)
