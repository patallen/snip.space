from app.models import Language
from flask import url_for
from app import app


def populate_choice_field(form, current_user=None):
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


def url_for_page(request, page):
    """
    Wrapper for url_for function that merges the view_args with the
    url_args, updates the page number, and returns the resulting URL.

    This allows for users to navigate through pagination without losing
    sorting and ordering in the querystring.
    """
    view_args = request.view_args.copy()
    url_args = request.args.to_dict()
    args = view_args.copy()
    args.update(url_args)
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_page'] = url_for_page
    
