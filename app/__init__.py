#Initialize page
import os

from flask import Flask 
from datetime import timedelta
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

from flask_migrate import Migrate #database migration

#Create base directory
basedir = os.path.abspath(os.path.dirname(__file__))

#flask api session
app = Flask(__name__)
app.secret_key = "this-is-not-secret" #session data encrypted on server- this is to encrypt/decrypt data
app.permanent_session_lifetime = timedelta(days=1) #setting permanent session so user info stored for certain period of time/for easier access

#database - SQLAlchemy 
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)



#login
login = LoginManager(app)
login.login_view = 'login'

from app import route, models
