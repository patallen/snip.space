from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_envvar('SNIPSPACE_SETTINGS')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'danger'
#toolbar = DebugToolbarExtension(app)

from app import views
