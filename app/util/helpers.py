from app.models import Language, User

def populateChoiceField(form, current_user=None):
    """Populate the snippet form's language choicefield
    with languages from the database."""
    languages = [(lang.id, lang.display_text) for lang in Language.query.all()]
    form.language.choices = languages
