import os

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

ENVIRONMENT = "production"

app = Flask(__name__)
app.secret_key = str(os.urandom(16))
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
# Changes to the HTML files are reflected on the website without having to restart the Flask app.
app.jinja_env.auto_reload = True

if ENVIRONMENT == "production":
    database_uri = "postgresql://postgres:test1@localhost/website"
else:
    database_uri = "sqlite:///SQLite_database.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)

from flask_app import routes
