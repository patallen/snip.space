from flask_wtf import Form
from wtforms import TextAreaField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

class SnippetForm(Form):
    title = StringField('Title')
    snippet = TextAreaField('snippet', validators=[DataRequired()])

class SignupForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must mach.')])
    confirm = PasswordField('Confirm')
