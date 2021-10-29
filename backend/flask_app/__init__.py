import os

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

ENVIRONMENT = 'production'

app = Flask(__name__)
app.secret_key = str(os.urandom(16))
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
# Changes to the HTML files are reflected on the website without having to restart the Flask app.
app.jinja_env.auto_reload = True

if ENVIRONMENT == "production":
    database_uri = "postgresql://postgres:test1@localhost/website"
else: 
    database_uri = "sqlite:///sqlite-db.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)

os.makedirs("logs", exist_ok=True)
os.makedirs(os.path.join("flask_app", "uploads"), exist_ok=True)
os.makedirs(os.path.join("flask_app", "conversions"), exist_ok=True)
os.makedirs(os.path.join("flask_app", "ffmpeg-progress"), exist_ok=True)
os.makedirs(os.path.join("flask_app", "ffmpeg-output"), exist_ok=True)

from flask_app import views
