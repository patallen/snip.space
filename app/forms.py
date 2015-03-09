from flask_wtf import Form
from wtforms import TextAreaField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

def unique_username(form, field):
    if User.query.filter(User.username==field.data).first():
        raise ValidationError('Already taken.')

def unique_email(form, field):
    if User.query.filter(User.email==field.data).first():
        raise ValidationError('Already taken.')

class SnippetForm(Form):
    title = StringField('Title')
    snippet = TextAreaField('snippet', validators=[DataRequired()])

class SignupForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email(), unique_email])
    username = StringField('Username', validators=[DataRequired(), unique_username])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must mach.')])
    confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
