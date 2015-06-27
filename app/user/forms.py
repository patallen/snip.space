from app.models import User
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import ValidationError, DataRequired
from wtforms.validators import Email, Regexp, EqualTo


def unique_username(form, field):
    if User.query.filter(User.username == field.data).first():
        raise ValidationError('Already taken.')


def unique_email(form, field):
    if User.query.filter(User.email == field.data).first():
        raise ValidationError('Already taken.')


class SignupForm(Form):
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email(),
                                    unique_email])
    username = StringField('Username',
                           validators=[DataRequired(),
                                       unique_username,
                                       Regexp('^\w+$')])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         EqualTo('confirm',
                                         message='Passwords must match.')])
    confirm = PasswordField('Confirm Password')


class RequestResetForm(Form):
    email = StringField('Email Address', validators=[DataRequired(), Email()])


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class PasswordResetForm(Form):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired(),
                                 EqualTo('confirm',
                                         message='Passwords must match.')
                             ])
    confirm = PasswordField('Confirm Password')
