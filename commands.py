from flask.ext.script import Command, prompt, prompt_pass
from app import app, db
from app.models import User, Language
from datetime import datetime


languages = [
    ('', 'Text', '.txt'),
    ('clojure', 'Clojure', '.clj'),
    ('css', 'CSS', '.css'),
    ('clike', 'C/C++', '.cpp'),
    ('d', 'D', '.txt'),
    ('dart', 'Dart', '.dart'),
    ('erlang', 'Erlang', '.erl'),
    ('fortran', 'Fortran', '.txt'),
    ('go', 'Go', '.go'),
    ('haskell', 'Haskell', '.hs'),
    ('htmlmixed', 'HTML', '.html'),
    ('javascript', 'JavaScript', '.js'),
    ('lua', 'Lua', '.lua'),
    ('pascal', 'Pascal', '.pas'),
    ('perl', 'Perl', '.pl'),
    ('php', 'PHP', '.php'),
    ('python', 'Python', '.py'),
    ('r', 'R', '.txt'),
    ('ruby', 'Ruby', '.rb'),
    ('rust', 'Rust', '.rs'),
    ('shell', 'Shell', '.sh'),
    ('sql', 'SQL', '.sql'),
    ('xml', 'XML', '.xml'),
]


class CreateSuperuser(Command):
    """Creates a superuser in the database"""

    def run(self):
        username = prompt('Enter a username')
        email = prompt('Enter email address')
        password = prompt_pass('Enter password')
        confirm_password = prompt_pass('Enter password again')

        if password == confirm_password:
            try:
                user = User(username, email, password) 
                user.confirmed = True
                user.confirmed_date = datetime.utcnow()
                db.session.add(user)
                db.session.commit()
                print "Superuser '{}' has been created".format(username)
            except:
                print "Username and/or email already taken."
        else:
            print "Username and password do not match. Try again"


class SeedDatabase(Command):
    """Sets up database with seed data"""
    def add_lang(self, id, display, ext):
        try:
            lang = Language.query.get(id)
            lang.display_text = display
            lang.extension = ext
            db.session.add(lang)
        except:
            lang = Language(id, display, ext)
            db.session.add(lang)               

    def run(self):
        for lang in languages:
            self.add_lang(lang[0], lang[1], lang[2])
        db.session.commit()

        print "{} languages in the database".format(Language.query.count())
