from flask_wtf import Form
from wtforms import TextAreaField, StringField, BooleanField
from wtforms import PasswordField, SelectField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Regexp, Length
from app.models import User, Language


def unique_username(form, field):
    if User.query.filter(User.username==field.data).first():
        raise ValidationError('Already taken.')

def unique_email(form, field):
    if User.query.filter(User.email==field.data).first():
        raise ValidationError('Already taken.')


class SnippetForm(Form):
    title = StringField('Title')
    snippet = TextAreaField('snippet', validators=[DataRequired()])
    language = SelectField('language')
    private = BooleanField('Set Private?')

class SignupForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email(), unique_email])
    username = StringField('Username', validators=[DataRequired(), unique_username, Regexp('^\w+$')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match.')])
    confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class PreferencesForm(Form):
    language = SelectField('Default Syntax')

class DeleteForm(Form):
    delete = SubmitField('DELETE')

class RequestResetForm(Form):
    email = StringField('Email Address', validators=[DataRequired(), Email()])

class PasswordResetForm(Form):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match.')])
    confirm = PasswordField('Confirm Password')

class ChangePasswordForm(Form):
    newpw = PasswordField('New Password',
                          validators=[DataRequired(message="Both fields are required."),
                                      Length(min=8, message="Password must be atleast 8 characters."),
                                      EqualTo('confirmpw', message='Passwords do not match.')])
    confirmpw = PasswordField('Confirm New Password', validators=[DataRequired()])
