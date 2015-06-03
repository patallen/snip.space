from flask_wtf import Form
from wtforms import TextAreaField, StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

languages = [
    ('', 'Text'),
    ('clojure', 'Clojure'),
    ('css', 'CSS'),
    ('clike', 'C/C++'),
    ('d', 'D'),
    ('dart', 'Dart'),
    ('erlang', 'Erlang'),
    ('fortran', 'Fortran'),
    ('go', 'Go'),
    ('haskell', 'Haskell'),
    ('htmlmixed', 'HTML'),
    ('javascript', 'JavaScript'),
    ('lua', 'Lua'),
    ('pascal', 'Pascal'),
    ('perl', 'Perl'),
    ('php', 'PHP'),
    ('python', 'Python'),
    ('r', 'R'),
    ('ruby', 'Ruby'),
    ('rust', 'Rust'),
    ('shell', 'Shell'),
    ('sql', 'SQL'),
    ('xml', 'XML'),
]
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
