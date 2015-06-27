from flask_wtf import Form
from wtforms import PasswordField, SelectField
from wtforms.validators import Length, EqualTo, DataRequired


class PreferencesForm(Form):
    language = SelectField('Default Syntax')


class ChangePasswordForm(Form):
    newpw = PasswordField('New Password',
                          validators=[
                              DataRequired(
                                  message="Both fields are required."),
                              Length(
                                  min=8,
                                  message="Password must be 8 characters."),
                              EqualTo(
                                  'confirmpw',
                                  message='Passwords do not match.')])
    confirmpw = PasswordField('Confirm New Password',
                              validators=[DataRequired()])
