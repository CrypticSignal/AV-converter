from datetime import datetime
import json
import os
from time import time

from flask import render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename

from flask_app import app, db
import flask_app.converter as converter
from flask_app.models import ConverterDB
from flask_app.utils import delete_file, get_ip, log, log_this


def update_database():
    # Use the get_ip function imported from loggers.py
    user_ip = get_ip()
    # Query the database by IP.
    user = ConverterDB.query.filter_by(ip=user_ip).first()
    if user:
        user.times_used+= 1
        db.session.commit()
    else:
        new_user = ConverterDB(ip=user_ip, times_used=1)
        db.session.add(new_user)
        db.session.commit()


# This route is hit when a file has been uploaded.
@app.route("/api", methods=["POST"])
def homepage():
    uploaded_file = request.files["uploadedFile"]
    log_this(f"Uploaded {uploaded_file.filename}")
    log.info(uploaded_file)

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
    uploaded_file_path = os.path.join("flask_app", "uploads", secure_filename(input_filename))

    data = request.form["states"]

    chosen_codec = json.loads(data)["codec"]
    crf_value = json.loads(data)["crfValue"]
    is_keep_video = json.loads(data)["isKeepVideo"]
    opus_vorbis_slider = json.loads(data)["sliderValue"]
    video_mode = json.loads(data)["videoSetting"]

    output_name = request.form["outputName"]
    output_path = os.path.join("flask_app", "conversions", output_name)

    log.info(f"{input_filename} --> {output_name} [{chosen_codec}]")

    # These parameters are applicable no matter which codec was chosen.
    mutual_params = [session["progress_filename"], uploaded_file_path, output_path]

    # AAC
    if chosen_codec == "AAC":
        encoding_type = json.loads(data)["aacEncodingType"]
        bitrate = json.loads(data)["sliderValue"]
        vbr_quality = json.loads(data)["aacVbrMode"]
        params = [*mutual_params, is_keep_video, encoding_type, bitrate, vbr_quality]
        converter_result_dictionary = converter.aac(*params)
    # AC3
    elif chosen_codec == "AC3":
        ac3_bitrate = json.loads(data)["ac3Bitrate"]
        params = [*mutual_params, is_keep_video, ac3_bitrate]
        converter_result_dictionary = converter.ac3(*params)
    # ALAC
    elif chosen_codec == "ALAC":
        converter_result_dictionary = converter.alac(*mutual_params, is_keep_video)
    # CAF
    elif chosen_codec == "CAF":
        converter_result_dictionary = converter.caf(*mutual_params)
    # DTS
    elif chosen_codec == "DTS":
        dts_bitrate = json.loads(data)["dtsBitrate"]
        params = [*mutual_params, is_keep_video, dts_bitrate]
        converter_result_dictionary = converter.dts(*params)
    # FLAC
    elif chosen_codec == "FLAC":
        flac_compression = json.loads(data)["flacCompression"]
        params = [*mutual_params, is_keep_video, flac_compression]
        converter_result_dictionary = converter.flac(*params)
    # MKA
    elif chosen_codec == "MKA":
        converter_result_dictionary = converter.mka(*mutual_params)
    # MKV
    elif chosen_codec == "MKV":
        params = [*mutual_params, video_mode, crf_value]
        converter_result_dictionary = converter.mkv(*params)
    # MP3
    elif chosen_codec == "MP3":
        encoding_type = json.loads(data)["mp3EncodingType"]
        bitrate = json.loads(data)["sliderValue"]
        vbr_setting = json.loads(data)["mp3VbrSetting"]
        params = [*mutual_params, is_keep_video, encoding_type, bitrate, vbr_setting]
        converter_result_dictionary = converter.mp3(*params)
    # MP4
    elif chosen_codec == "MP4":
        params = [*mutual_params, video_mode, crf_value]
        converter_result_dictionary = converter.mp4(*params)
    # Opus
    elif chosen_codec == "Opus":
        cbr_bitrate = json.loads(data)["sliderValue"]
        encoding_type = json.loads(data)["opusEncodingType"]
        params = [*mutual_params, encoding_type, opus_vorbis_slider, cbr_bitrate]
        converter_result_dictionary = converter.opus(*params)
    # Vorbis
    elif chosen_codec == "Vorbis":
        encoding_type = json.loads(data)["vorbisEncodingType"]
        quality_level = json.loads(data)["qValue"]
        params = [*mutual_params, encoding_type, quality_level, opus_vorbis_slider]
        converter_result_dictionary = converter.vorbis(*params)
    # WAV
    elif chosen_codec == "WAV":
        wav_bit_depth = json.loads(data)["wavBitDepth"]
        params = [*mutual_params, is_keep_video, wav_bit_depth]
        converter_result_dictionary = converter.wav(*params)

    # The 'error' key is set to None if the file converted successfully.
    if converter_result_dictionary["error"] is None:
        update_database()
        return converter_result_dictionary
    # Return a 500 error if the file conversion was not successful.
    else:
        return converter_result_dictionary, 500


@app.route("/api/ffmpeg-progress/<filename>", methods=["GET"])
def get_file(filename):
    return send_from_directory("ffmpeg-progress", filename)


@app.route("/api/flask_app/ffmpeg-output/<filename>", methods=["GET"])
def view_ffmpeg_output(filename):
    log.info(filename)
    log.info('IN DFJDSKH')
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
    else:
        log.info(f'{datetime.now().strftime("[%H:%M:%S]")} {filename}')
    finally:
        delete_file(os.path.join("flask_app", "conversions", filename))


@app.route("/game")
def game():
    return render_template("game.html")