from datetime import datetime
import json
import os
from time import time

from flask import render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename

from flask_app import app, db
from flask_app.converter import run_converter
from flask_app.utils import delete_file, log, log_this, update_database


# This route is hit when a file has been uploaded.
@app.route("/api", methods=["POST"])
def homepage():
    uploaded_file = request.files["uploadedFile"]
    log_this(f"Uploaded {uploaded_file.filename}")
    update_database()

    filename_secure = secure_filename(uploaded_file.filename)
    # Save the uploaded file to the uploads folder.
    uploaded_file.save(os.path.join("flask_app/uploads", filename_secure))

    session["progress_filename"] = f"{str(time())[:-8]}.txt"
    with open(os.path.join("flask_app", "ffmpeg-progress", session["progress_filename"]), "w"):
        pass

    return os.path.join("api", "ffmpeg-progress", session["progress_filename"])


@app.route("/api/convert", methods=["POST"])
def convert_file():
    input_filename = request.form["inputFilename"]
    os.makedirs("flask_app/uploads", exist_ok=True)
    uploaded_file_path = os.path.join("flask_app", "uploads", secure_filename(input_filename))

    data = json.loads(request.form["states"])
    
    chosen_codec = data["codec"]
    slider_value = data["sliderValue"]
    is_keep_video = data["isKeepVideo"]

    os.makedirs("flask_app/conversions", exist_ok=True)
    output_path = os.path.join("flask_app", "conversions", request.form["outputName"])

    log.info(f"{input_filename} --> {request.form['outputName']} [{chosen_codec}]")

    # These parameters are applicable no matter which codec was chosen.
    mutual_params = [session["progress_filename"], uploaded_file_path, output_path]

    converter_result = run_converter(chosen_codec, mutual_params, is_keep_video, data, slider_value)

    # The 'error' key is set to None if the file converted successfully.
    if converter_result["error"] is None:
        return converter_result
    # Return a 500 error if the file conversion was not successful.
    else:
        return converter_result, 500


@app.route("/api/ffmpeg-progress/<filename>", methods=["GET"])
def get_file(filename):
    return send_from_directory("ffmpeg-progress", filename)


@app.route("/api/flask_app/ffmpeg-output/<filename>", methods=["GET"])
def view_ffmpeg_output(filename):
    return send_from_directory("ffmpeg-output", filename)


@app.route("/api/flask_app/conversions/<filename>", methods=["GET"])
def send_file(filename):
    mimetype_value = "audio/mp4" if os.path.splitext(filename)[1] == ".m4a" else ""
    try:
        return send_from_directory(
            "conversions", filename, mimetype=mimetype_value, as_attachment=True
        )
    except Exception as e:
        log.info(f"Unable to return the converted file:\n{e}")
    finally:
        delete_file(os.path.join("flask_app", "conversions", filename))


@app.route("/game")
def game():
    return render_template("game.html")