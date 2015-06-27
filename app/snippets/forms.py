from flask_wtf import Form
from wtforms import TextAreaField, StringField, BooleanField
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


class SnippetForm(Form):
    title = StringField('Title')
    snippet = TextAreaField('snippet', validators=[DataRequired()])
    language = SelectField('language')
    private = BooleanField('Set Private?')


class DeleteForm(Form):
    delete = SubmitField('DELETE')
