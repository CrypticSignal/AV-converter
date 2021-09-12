from datetime import datetime
import os
from pathlib import Path
from time import time

from flask import Blueprint, Flask, request, send_from_directory, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from youtube_dl import YoutubeDL

from loggers import get_ip, log, log_downloads_per_day, log_this
from utils import clean_up, delete_file, empty_folder

yt = Blueprint("yt", __name__)
app = Flask(__name__)

SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

os.makedirs("yt-progress", exist_ok=True)
os.makedirs("downloads", exist_ok=True)
download_dir = "downloads"
unwanted_filetypes = [".part", ".jpg", ".ytdl", ".webp"]


def update_database(mb_downloaded):
    # Use the get_ip function imported from loggers.py
    user_ip = get_ip()
    # Query the database by IP.
    user = User.query.filter_by(ip=user_ip).first()
    if user:
        user.times_used_yt_downloader += 1
        user.mb_downloaded += mb_downloaded
        db.session.commit()
    else:
        new_user = User(ip=user_ip, times_used_yt_downloader=1, mb_downloaded=0)
        db.session.add(new_user)
        db.session.commit()


def run_youtube_dl(video_link, options):
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(video_link, download=False)

    session["filename_stem"] = Path(ydl.prepare_filename(info)).stem

    try:
        ydl.download([video_link])
    except Exception as error:
        log.info(f'Error downloading {session["filename_stem"]}:\n{error}')
        return str(error), 500
    else:
        log_downloads_per_day()

    return True


def return_download_path():
    filename = [
        file
        for file in os.listdir(download_dir)
        if Path(file).suffix not in unwanted_filetypes
        and Path(file).stem == session["filename_stem"]
    ][0]

    filesize = round((os.path.getsize(os.path.join(download_dir, filename)) / 1_000_000), 2)
    update_database(filesize)

    # Remove any hashtags or pecentage symbols as they cause an issue and make the filename more aesthetically pleasing.
    new_filename = filename.replace("#", "").replace("%", "").replace("_", " ")

    try:
        # Rename the file.
        os.replace(
            os.path.join(download_dir, filename),
            os.path.join(download_dir, new_filename),
        )
    except Exception as e:
        log.info(f"Unable to rename {filename} to {new_filename}:\n{e}")
        clean_up(Path(filename).stem)
    else:
        log.info(f"{new_filename} | {filesize} MB")
        clean_up(Path(new_filename).stem)

        # Update the list of videos downloaded.
        with open("logs/downloads.txt", "a") as f:
            f.write(f"\n{new_filename}")

        # Return the download link.
        return os.path.join("api", "downloads", new_filename)


class Logger:
    def debug(self, msg):
        with open(session["progress_file_path"], "a") as f:
            try:
                f.write(f"{msg}\n")
            except Exception as e:
                log.info("Unable to write YT progress to file:\n{e}")

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


# This class is a table in the database.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20), unique=True, nullable=False)
    times_used_yt_downloader = db.Column(db.Integer, default=0)
    mb_downloaded = db.Column(db.Float, default=0)

    def __init__(self, ip, times_used_yt_downloader, mb_downloaded):
        self.ip = ip
        self.times_used_yt_downloader = times_used_yt_downloader
        self.mb_downloaded = mb_downloaded


# Initialization
db.create_all()
downloads_today = 0


@yt.route("/api/yt", methods=["POST"])
def yt_downloader():
    # First POST request:
    if request.form["button_clicked"] == "yes":
        progress_file_name = f"{str(time())[:-8]}.txt"
        session["progress_file_path"] = f"yt-progress/{progress_file_name}"
        return session["progress_file_path"], 200

    # Second POST request:

    log_this(f'Clicked on {request.form["button_clicked"]}')

    user_ip = get_ip()
    # Query the database by IP.
    user = User.query.filter_by(ip=user_ip).first()
    if user:
        string = (
            f"{user.times_used_yt_downloader} times"
            if user.times_used_yt_downloader > 1
            else "once"
        )
        log.info(f"This user has used the downloader {string} before.")

    video_link = request.form["link"]
    log.info(video_link)

    # Video (best quality)
    if request.form["button_clicked"] == "video_best":
        options = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "restrictfilenames": True,
            "logger": Logger(),
        }

        result = run_youtube_dl(video_link, options)

        if result == True:
            return return_download_path()

        return result

    # MP4
    elif request.form["button_clicked"] == "mp4":
        options = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "restrictfilenames": True,
            "logger": Logger(),
        }

        result = run_youtube_dl(video_link, options)

        if result == True:
            return return_download_path()

        return result

    # Audio (best quality)
    elif request.form["button_clicked"] == "audio_best":
        options = {
            "format": "bestaudio/best",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "postprocessors": [{"key": "FFmpegExtractAudio"}],
            "restrictfilenames": True,
            "logger": Logger(),
        }

        result = run_youtube_dl(video_link, options)

        if result == True:
            return return_download_path()

        return result

    # MP3
    elif request.form["button_clicked"] == "audio_mp3":
        options = {
            "format": "bestaudio/best",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "writethumbnail": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "0",
                },
                {"key": "EmbedThumbnail"},
            ],
            "restrictfilenames": True,
            "logger": Logger(),
        }

        result = run_youtube_dl(video_link, options)

        if result == True:
            return return_download_path()

        return result


# This is where the youtube-dl progress file is.
@yt.route("/api/yt-progress/<filename>")
def get_file(filename):
    return send_from_directory("yt-progress", filename)


@yt.route("/api/downloads/<filename>", methods=["GET"])
def send_file(filename):
    mimetype_value = "audio/mp4" if Path(filename).suffix == ".m4a" else ""
    try:
        return send_from_directory(download_dir, filename, mimetype=mimetype_value)
    finally:
        delete_file(os.path.join("downloads", filename))
