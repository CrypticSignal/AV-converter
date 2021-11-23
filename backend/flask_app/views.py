from datetime import datetime
import json
import os
from pathlib import Path
from time import time

from flask import render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename

from flask_app import app, db
from flask_app.converter import run_converter
from flask_app.models import DownloaderDB
from flask_app.utils import delete_file, detailed_log, get_ip, update_converter_database
from flask_app.yt_downloader import return_download_path, run_yt_downloader
from logger import log

# This route is hit when a file has been uploaded.
@app.route("/api", methods=["GET", "POST"])
def homepage():
    uploaded_file = request.files["uploadedFile"]
    detailed_log(f"Uploaded {uploaded_file.filename}")
    update_converter_database()

    filename_secure = secure_filename(uploaded_file.filename)
    # Save the uploaded file to the uploads folder.
    uploaded_file.save(os.path.join("uploads", filename_secure))

    session["ffmpeg_progress_url"] = str(time())[:-8] + ".txt"
    return os.path.join("api", "ffmpeg_progress", session["ffmpeg_progress_url"])


@app.route("/api/convert", methods=["POST"])
def convert_file():
    input_filename = request.form["inputFilename"]
    uploaded_file_path = os.path.join("uploads", secure_filename(input_filename))

    data = json.loads(request.form["states"])
    chosen_codec = data["codec"]
    slider_value = data["sliderValue"]
    is_keep_video = data["isKeepVideo"]

    output_path = os.path.join("conversions", request.form["outputName"])

    log.info(f"{input_filename} --> {request.form['outputName']} [{chosen_codec}]")

    # These parameters are applicable no matter which codec was chosen.
    mutual_params = [session["ffmpeg_progress_url"], uploaded_file_path, output_path]

    converter_result = run_converter(chosen_codec, mutual_params, is_keep_video, data, slider_value)

    # The 'error' key is set to None if the file converted successfully.
    if converter_result["error"] is None:
        return converter_result
    # Return a 500 error if the file conversion was not successful.
    else:
        return converter_result, 500


@app.route("/api/ffmpeg_progress/<filename>", methods=["GET"])
def get_file(filename):
    return send_from_directory("../ffmpeg_progress", filename)


@app.route("/api/ffmpeg_output/<filename>", methods=["GET"])
def view_ffmpeg_output(filename):
    return send_from_directory("../ffmpeg_output", filename)


@app.route("/api/conversions/<filename>", methods=["GET"])
def send_file(filename):
    mimetype_value = "audio/mp4" if os.path.splitext(filename)[1] == ".m4a" else ""
    try:
        return send_from_directory(
            "../conversions", filename, mimetype=mimetype_value, as_attachment=True
        )
    except Exception as e:
        log.error(f"Unable to return the converted file:\n{e}")
    finally:
        delete_file(os.path.join("conversions", filename))


# YOUTUBE DOWNLOADER:


@app.route("/api/yt", methods=["POST"])
def yt_downloader():
    # First POST request:
    if request.form["button_clicked"] == "yes":
        ffmpeg_progress_url = str(time())[:-8] + ".txt"
        session["yt_progress_url"] = os.path.join("yt_progress", ffmpeg_progress_url)
        with open(session["yt_progress_url"], "x"):  pass
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
