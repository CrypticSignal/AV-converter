import os

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = str(os.urandom(16))
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
# Set the maximum upload size to 3 GB.
max_upload_size = 3  # in GB.
app.config["MAX_CONTENT_LENGTH"] = max_upload_size * 1000 * 1000 * 1000
# Changes to the HTML files are reflected on the website without having to restart the Flask app.
app.jinja_env.auto_reload = True

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:test1@localhost/website"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)

os.makedirs("flask_app/uploads", exist_ok=True)
os.makedirs("flask_app/conversions", exist_ok=True)
os.makedirs("flask_app/ffmpeg-progress", exist_ok=True)
os.makedirs("flask_app/ffmpeg-output", exist_ok=True)

from flask_app import views