from app import db
from app.models import User, Language

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

def populate():
	db.drop_all()
	db.create_all()
	for lang in languages:
		add_lang(lang[0], lang[1], lang[2])

	add_user("pat", 'password', 'prallen90@gmail.com')
	db.session.commit()

def print_langs():
	langs = Language.query.all()
	for lang in langs:
		print(lang)

def add_lang(id, display, ext):
	lang = Language(id, display, ext)
	db.session.add(lang)
	return lang

def add_user(un, pw, email):
	user = User(un, email, pw)
	db.session.add(user)
	return user

if __name__ == '__main__':
	populate()
	print_langs()
