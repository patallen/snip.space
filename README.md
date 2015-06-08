## Snipstr
A user-based snippet/text respository. Keep track of and share all of your random snippets.

## Instructions
1. Clone the repository `git clone https://github.com/patallen/snip.space.git`
1. Create virtualenv in main directory: `virtualenv venv` (python 2.7)
1. Install python dependencies: `pip install -r requirements.txt`
1. Create postgres database
1. Create settings file that includes:
	- SECRET_KEY
	- SQLALCHEMY_DATABASE_URI
	- DEBUG
	- HASHID_SALT
	- HASHID_LEN
1. `export SNIPSPACE_SETTINGS=/path/to/settings/file`
1. Populate database with seed data `python populate_db.py`
1. To run server: `python manage.py runserver -dr`

## TODO:
- [ ] Flash messages
- [ ] Ability to edit snippets 
- [ ] Private snippets
- [ ] Make snippets downloadable
- [ ] Report snippet functionality
- [ ] Ability to sort snippets on user page
- [ ] Email verification and password reset
- [ ] Statistics page
- [x] Implement PostgreSQL Database
- [x] Snippet view count
- [x] Flask-login for sessions
- [x] Member pages
- [x] Implement UUID functionality
- [x] Create 'add snippet' page.
- [x] Create 'view snippet' page.
- [x] Create Snippet model
- [x] Create User model
- [x] Implement user sign-up w/ password hashing
