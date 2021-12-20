from datetime import datetime
import json
import os
from pathlib import Path
from time import time

from flask import render_template, request, send_file, send_from_directory, session
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
        session["yt_progress_url"] = str(time())[:-8] + ".txt"

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
@app.route("/api/<filename>")
def get_progress_file(filename):
    if os.path.isfile(filename):
        return send_file(f"../{filename}")
    return ""


@app.route("/api/download/<filename>", methods=["GET"])
def send_download(filename):
    mimetype_value = "audio/mp4" if Path(filename).suffix == ".m4a" else ""
    try:
        if os.path.isfile(f"../{filename}"):
            return send_file(f"../../{filename}", mimetype=mimetype_value, as_attachment=True)
        # On mobile, when using Chrome/Samsung Internet, for some reason the send_download function is hit multiple times.
        # We need to return a response after the file has been deleted otherwise there will be the following error:
        # "The function either returned None or ended without a return statement."
        return ""
    finally:
        delete_file(f"../{filename}")


# GAME:


@app.route("/game")
def game():
    return render_template("game.html")


@app.route("/node_modules/@ffmpeg/core/dist/ffmpeg-core.worker.js")
def send_ffmpeg_core_worker():
    return send_file(
        "../../frontend/node_modules/@ffmpeg/core/dist/ffmpeg-core.worker.js",
        mimetype="application/javascript",
    )


@app.route("/node_modules/@ffmpeg/core/dist/ffmpeg-core.js")
def send_ffmpeg_core():
    return send_file(
        "../../frontend/node_modules/@ffmpeg/core/dist/ffmpeg-core.js",
        mimetype="application/javascript",
    )


@app.route("/node_modules/@ffmpeg/core/dist/ffmpeg-core.wasm")
def send_ffmpeg_core_wasm():
    return send_file(
        "../../frontend/node_modules/@ffmpeg/core/dist/ffmpeg-core.wasm",
        mimetype="application/wasm",
    )
