from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt
from celery import Celery 

app = Flask(__name__)
app.config.from_envvar('SNIPSPACE_SETTINGS')

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'danger'
from app.user.views import user
from app.snippets.views import snippets
from app.settings.views import settings

app.register_blueprint(user)
app.register_blueprint(snippets)
app.register_blueprint(settings)


from app import views
