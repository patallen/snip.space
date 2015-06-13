from app.models import Language

def populateChoiceField(form):
    """Populate the snippet form's language choicefield
    with languages from the database."""
    languages = [(lang.id, lang.display_text) for lang in Language.query.all()]
    form.language.choices = languages