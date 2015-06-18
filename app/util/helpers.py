from app.models import Language, User

def populateChoiceField(form, current_user=None):
    """Populate the snippet form's language choicefield
    with languages from the database."""
    languages = [(lang.id, lang.display_text) for lang in Language.query.all()]
    form.language.choices = languages

    # Sort languages and put Text first
    languages.sort()
    for i, lang in enumerate(languages):
        if lang[0] == 'text':
            text = languages.pop(i)
            languages.insert(0, text)
            break
    form.language.choices = languages
