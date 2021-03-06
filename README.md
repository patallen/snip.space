## snip.space
An ad-free, free, and open source user-based code snippet/text respository. Sign up and keep track of and share all of your random snippets.

Check out the live version of the site at [snip.space](http://snip.space/).


## Instructions
1. Clone the repository `git clone https://github.com/patallen/snip.space.git`
1. Create a python 2.7 virtualenv in main directory: `mkvirtualenv snipspace`
1. `$ bower install `
1. Install python dependencies: `pip install -r requirements.txt`
1. Create postgres database
1. Create settings file based off of default_settings.py
	- Place outside of project dir: ex `~/settings/snipspace.py`
	- `export SNIPSPACE_SETTINGS=~/settings/snipspace.py`
1. `python manage.py db upgrade`
1. Seed database: `python manage.py seed`
1. Create superuser: `python manage.py createsuperuser`
1. To run server: `python manage.py runserver`

## TODO:
- [ ] ToS
- [ ] Privacy Policy
- [ ] Track anonymous users
- [ ] Admin portal
- [ ] Report snippet functionality
- [ ] Statistics page
- [x] Fork Snippet Functionality
- [x] About page
- [x] Popular Snippets timeframe macro
- [x] User settings page (started)
- [x] Implement Blueprints
- [x] Trending/Popular by timeframe page
- [x] Remove flash message redundancy
- [x] Password reset functionality
- [x] Pagination macro
- [x] Recent Snippets Page
- [x] Celery task queue for emails and ..?
- [x] Ability to sort snippets on user page
- [x] User snippet pagination
- [x] Private snippets
- [x] Custom 404 exceptions and pages
- [x] CreateSuperuser manager script
- [x] Add flash messages
- [x] Email verification
- [x] Ability to edit snippets 
- [x] Make downloaded files use proper extension
- [x] Make snippets downloadable
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
