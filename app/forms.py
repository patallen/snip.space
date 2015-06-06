from flask_wtf import Form
from wtforms import TextAreaField, StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Language

languages = [(lang.id, lang.display_text) for lang in Language.query.all()]

def unique_username(form, field):
    if User.query.filter(User.username==field.data).first():
        raise ValidationError('Already taken.')

def unique_email(form, field):
    if User.query.filter(User.email==field.data).first():
        raise ValidationError('Already taken.')

class SnippetForm(Form):
    title = StringField('Title')
    snippet = TextAreaField('snippet', validators=[DataRequired()])
    language = SelectField('language', choices=languages)

class SignupForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email(), unique_email])
    username = StringField('Username', validators=[DataRequired(), unique_username])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must mach.')])
    confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class DeleteForm(Form):
    delete = SubmitField('DELETE')
