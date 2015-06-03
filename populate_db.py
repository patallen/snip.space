from app import db
from app.models import User, Language

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

def populate():
	db.drop_all()
	db.create_all()
	for lang in languages:
		add_lang(lang[0], lang[1])

	add_user("pat", 'password', 'prallen90@gmail.com')
	db.session.commit()

def print_langs():
	langs = Language.query.all()
	for lang in langs:
		print(lang)

def add_lang(id, display):
	lang = Language(id, display)
	db.session.add(lang)
	return lang

def add_user(un, pw, email):
	user = User(un, email, pw)
	db.session.add(user)
	return user

if __name__ == '__main__':
	populate()
	print_langs()