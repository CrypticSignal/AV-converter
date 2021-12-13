from datetime import datetime
import json
import os
from pathlib import Path
from time import time

from flask import render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename

from flask_app import app, db
from flask_app.create_ffmpeg_args import get_ffmpeg_args
from flask_app.models import DownloaderDB
from flask_app.utils import delete_file, detailed_log, get_ip, update_converter_database
from flask_app.yt_downloader import return_download_path, run_yt_downloader
from logger import log


@app.route("/api/get-ffmpeg-args", methods=["POST"])
def convert_file():
    data = json.loads(request.form["state"])
    input_filename = data["inputFilename"]
    detailed_log(f"| {input_filename}")
    output_name = data["outputName"]
    chosen_codec = data["codec"]
    slider_value = data["sliderValue"]
    is_keep_video = data["isKeepVideo"]

    update_converter_database()

    return get_ffmpeg_args(chosen_codec, output_name, is_keep_video, data, slider_value)


# YOUTUBE DOWNLOADER:


@app.route("/api/yt", methods=["POST"])
def yt_downloader():
    # First POST request:
    if request.form["button_clicked"] == "yes":
        ffmpeg_progress_url = str(time())[:-8] + ".txt"
        session["yt_progress_url"] = os.path.join("yt_progress", ffmpeg_progress_url)
        with open(session["yt_progress_url"], "x"):
            pass
        return session["yt_progress_url"], 200

    # Second POST request:

    detailed_log(f'Clicked on {request.form["button_clicked"]}')

    # Query the database by IP.
    user = DownloaderDB.query.filter_by(ip=get_ip()).first()
    if user:
        string = f"{user.times_used} times" if user.times_used > 1 else "once"
        log.info(f"This user has used the downloader {string} before.")

    video_link = request.form["link"]
    log.info(video_link)

    result = run_yt_downloader(request.form, video_link)

    if result == True:
        return return_download_path()

    return result


# This is where the youtube-dl progress file is.
@app.route("/api/yt_progress/<filename>")
def get_progress_file(filename):
    return send_from_directory("../yt_progress", filename)


@app.route("/api/downloads/<filename>", methods=["GET"])
def send_download(filename):
    mimetype_value = "audio/mp4" if Path(filename).suffix == ".m4a" else ""
    try:
        # isfile() is from the perspective of run.py hence the path is "downloads" rather than "../downloads"
        if os.path.isfile(os.path.join("downloads", filename)):
            return send_from_directory(
                "../downloads", filename, mimetype=mimetype_value, as_attachment=True
            )
        # On mobile, when using Chrome/Samsung Internet, for some reason the send_download function is hit multiple times.
        # We need to return a response after the file has been deleted otherwise there will be the following error:
        # "The function either returned None or ended without a return statement."
        else:
            return ""
    finally:
        delete_file(os.path.join("downloads", filename))


# GAME:


@app.route("/game")
def game():
    return render_template("game.html")
