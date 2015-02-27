from flask_wtf import Form
from wtforms import TextAreaField, StringField
from wtforms.validators import DataRequired

class SnippetForm(Form):
    title = StringField('Title')
    snippet = TextAreaField('snippet', validators=[DataRequired()])
