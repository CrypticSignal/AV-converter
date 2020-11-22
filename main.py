from datetime import datetime
import os
from time import time

from flask import Flask, render_template, request, send_from_directory, session
from flask_session import Session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

import converter  # converter.py
from loggers import log, log_this, log_visit
from trimmer import trimmer  # Importing the blueprint in trimmer.py
from yt import yt  # Importing the blueprint in yt.py

app = Flask(__name__)
secret_key = str(os.urandom(16))
app.secret_key = secret_key
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Set the maximum upload size to 3 GB.
max_upload_size = 3  # in GB.
app.config['MAX_CONTENT_LENGTH'] = max_upload_size * 1000 * 1000 * 1000
# Changes to the HTML files are reflected on the website without having to restart the Flask app.
app.jinja_env.auto_reload = True

app.register_blueprint(yt)
app.register_blueprint(trimmer)

# The database object (db) needs to be defined in main.py even though we're not using the database in main.py
# Otherwise you get the following error:
# "AssertionError: The sqlalchemy extension was not registered to the current application."
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# For the chat section of the website.
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

os.makedirs('uploads', exist_ok=True)
os.makedirs('conversions', exist_ok=True)


def run_converter(codec, params):
    codec_to_converter = {
                            "aac": converter.aac,
                            "ac3": converter.ac3,
                            "alac": converter.alac,
                            "dts": converter.dts,
                            "flac": converter.flac,
                            "mka": converter.mka,
                            "mkv": converter.mkv,
                            "mp3": converter.mp3,
                            "mp4": converter.mp4,
                            "opus": converter.opus,
                            "vorbis": converter.vorbis,
                            "wav": converter.wav
    }
    return codec_to_converter[codec](*params)


def clean_up():
    os.remove(f'uploads/{session["uploaded_file"]}')
    log.info(f'Deleted uploads/{session["uploaded_file"]}')
    os.remove(f'conversions/{session["converted_file_name"]}')
    log.info(f'Deleted conversions/{session["converted_file_name"]}')


# When a file has been uploaded, a POST request is sent to the homepage.
@app.route('/', methods=['POST'])
def homepage():
    if request.data:
        log_this('Clicked on the convert button.')
        return 'is_convert_clicked received.'

    elif 'upload_progress' in request.form: 
        log.info(f'{datetime.now().strftime("[%H:%M:%S]")} {request.form["upload_progress"]}% uploaded...')
        return request.form['upload_progress']

    elif request.form["request_type"] == "convert_url":
        session['progress_filename'] = f'{str(time())[:-8]}.txt'
        return session['progress_filename']

    elif request.form["request_type"] == "uploaded":
        upload_time = datetime.now().strftime('%H:%M:%S')
        log.info(f'Upload complete at {upload_time}')
        uploaded_file = request.files["chosen_file"]
        session['uploaded_file'] = uploaded_file.filename
        filesize = request.form["filesize"]
        log.info(uploaded_file)
        log.info(f'Size: {filesize} MB')
        # Make the filename safe.
        filename_secure = secure_filename(uploaded_file.filename)
        # Save the uploaded file to the uploads folder.
        uploaded_file.save(os.path.join("uploads", filename_secure))

        conversion_progress_filename = f'{str(time())[:-8]}.txt'
        session['progress_filename'] = conversion_progress_filename
        return session['progress_filename']

    elif request.form["request_type"] == "convert":
        filename = request.form["filename"]

        if 'http' in filename and '://' in filename:
            uploaded_file_path = filename
        else:
            uploaded_file_path = os.path.join("uploads", secure_filename(filename))

        chosen_codec = request.form["chosen_codec"]
        crf_value = request.form["crf_value"]
        video_mode = request.form["video_mode"]
        is_keep_video = request.form["is_keep_video"]
        # MP3
        mp3_encoding_type = request.form["mp3_encoding_type"]
        mp3_bitrate = request.form["mp3_bitrate"]
        mp3_vbr_setting = request.form["mp3_vbr_setting"]
        # AAC
        fdk_type = request.form["fdk_type"]
        fdk_cbr = request.form["fdk_cbr"]
        fdk_vbr = request.form["fdk_vbr"]
        is_fdk_lowpass = request.form["is_fdk_lowpass"]
        fdk_lowpass = request.form["fdk_lowpass"]
        # Vorbis
        vorbis_encoding = request.form["vorbis_encoding"]
        vorbis_quality = request.form["vorbis_quality"]
        # Vorbis/Opus
        opus_vorbis_slider = request.form["opus_vorbis_slider"]
        # AC3
        ac3_bitrate = request.form["ac3_bitrate"]
        # FLAC
        flac_compression = request.form["flac_compression"]
        # DTS
        dts_bitrate = request.form["dts_bitrate"]
        # Opus
        opus_cbr_bitrate = request.form["opus_cbr_bitrate"]
        opus_encoding_type = request.form["opus_encoding_type"]
        # WAV
        wav_bit_depth = request.form["wav_bit_depth"]
        # Desired filename
        output_name = request.form["output_name"]

        log.info(f'They chose {chosen_codec} | Output Filename: {output_name}')
        output_path = os.path.join('conversions', output_name)
        extension = None

        # AAC
        if chosen_codec == 'AAC':
            params = [session['progress_filename'], uploaded_file_path, is_keep_video, fdk_type, fdk_cbr,
                      fdk_vbr, is_fdk_lowpass, fdk_lowpass, output_path]
            extension = run_converter('aac', params)

        # AC3
        elif chosen_codec == 'AC3':
            params = [session['progress_filename'], uploaded_file_path, is_keep_video, ac3_bitrate, output_path]
            extension = run_converter('ac3', params)

        # ALAC
        elif chosen_codec == 'ALAC':
            params = [session['progress_filename'], uploaded_file_path, is_keep_video, output_path]
            extension = run_converter('alac', params)

        # CAF
        elif chosen_codec == 'CAF':
            params = [session['progress_filename'], uploaded_file_path, output_path]
            extension = run_converter('caf', params)

        # DTS
        elif chosen_codec == 'DTS':
            params = [session['progress_filename'], uploaded_file_path, is_keep_video, dts_bitrate, output_path]
            extension = run_converter('dts', params)

        # FLAC
        elif chosen_codec == 'FLAC':
            params = [session['progress_filename'], uploaded_file_path, is_keep_video, flac_compression,
                      output_path]
            extension = run_converter('flac', params)

        # MKA
        elif chosen_codec == 'MKA':
            params = [session['progress_filename'], uploaded_file_path, output_path]
            extension = run_converter('mka', params)

        # MKV
        elif chosen_codec == 'MKV':
            params = [session['progress_filename'], uploaded_file_path, video_mode, crf_value, output_path]
            extension = run_converter('mkv', params)

        # MP3
        elif chosen_codec == 'MP3':
            params = [session['progress_filename'], uploaded_file_path, is_keep_video, mp3_encoding_type,
                      mp3_bitrate, mp3_vbr_setting, output_path]
            extension = run_converter('mp3', params)

        # MP4
        elif chosen_codec == 'MP4':
            params = [session['progress_filename'], uploaded_file_path, video_mode, crf_value, output_path]
            extension = run_converter('mp4', params)

        # Opus
        elif chosen_codec == 'Opus':
            params = [session['progress_filename'], uploaded_file_path, opus_encoding_type, opus_vorbis_slider,
                      opus_cbr_bitrate, output_path]
            extension = run_converter('opus', params)

        # Vorbis
        elif chosen_codec == 'Vorbis':
            params = [session['progress_filename'], uploaded_file_path, vorbis_encoding, vorbis_quality,
                      opus_vorbis_slider, output_path]
            extension = run_converter('vorbis', params)

        # WAV
        elif chosen_codec == 'WAV':
            params = [session['progress_filename'], uploaded_file_path, is_keep_video, wav_bit_depth,
                      output_path]
            extension = run_converter('wav', params)

        possible_extensions = ['.aac', '.ac3', '.dts', '.flac', '.mka', '.mkv', '.mp3', '.mp4', '.ogg', '.opus', '.wav']
        if extension['error'] is not None:
            return extension, 500
        else:
            log.info('in else main')
            # Filename after conversion.
            session['converted_file_name'] = f'{output_name}{extension["ext"]}'
            return extension


@app.route("/ffmpeg-progress/<filename>")
def get_file(filename):
    return send_from_directory('ffmpeg-progress', filename)


@app.route("/ffmpeg_output/<filename>")
def get_ffmpeg_output(filename):
    log.info(filename)
    return send_from_directory('ffmpeg_output', filename)


# app.js directs the user to this URL when the conversion is complete.
@app.route("/conversions/<filename>", methods=["GET"])
def send_file(filename):
    log.info(f'{datetime.now().strftime("[%H:%M:%S]")} https://free-av-tools.com/conversions/{filename}')
    mimetype_value = 'audio/mp4' if os.path.splitext(filename)[1] == ".m4a" else ''
    try:
        return send_from_directory('conversions', filename, mimetype=mimetype_value, as_attachment=True)
    except Exception as error:
        log.error(f'Unable to send conversions/{filename}. Error: \n{error}')
    finally:
        clean_up()

    
# Game 1
@app.route("/game", methods=['POST'])
def return_world_record():
    current_datetime = datetime.now().strftime('%d-%m-%y at %H:%M:%S')
    user = request.environ.get("HTTP_X_REAL_IP").split(',')[0]
    user_agent = request.headers.get('User-Agent')
    score = request.form['score']
    times_missed = request.form['times_missed']
    canvas_width = request.form['canvas_width']
    canvas_height = request.form['canvas_height']
    try:
        int(score)
        int(times_missed)
        int(canvas_width)
        int(canvas_height)
    except ValueError:
        log.error("[Game 1] The user changed something to a non-int.")
    else:
        os.makedirs('GameScores', exist_ok=True)
        with open("GameScores/HighScores.txt", "a") as f:
                f.write(f'{score} | {times_missed} | {user} | {user_agent} | {canvas_width}'
                        f'x{canvas_height} | {current_datetime}\n')
    finally:
        just_scores = []
        with open('GameScores/HighScores.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                just_scores.append(line.split('|')[0].strip())
        return ''


# Game 2
@app.route("/game2", methods=['POST'])
def save_game2_stats():
    current_datetime = datetime.now().strftime('%d-%m-%y at %H:%M:%S')
    user = request.environ.get("HTTP_X_REAL_IP").split(',')[0]
    user_agent = request.headers.get('User-Agent')
    reaction_time = request.form['reaction_time']
    try:
        int(reaction_time)
    except ValueError:
        log.error("[Game 2] The user changed reaction_time to a non-int.")
    else:
        os.makedirs('GameScores', exist_ok=True)
        with open("GameScores/ReactionTimes.txt", "a") as f:
            f.write(f'{reaction_time} ms | {user} | {user_agent} | {current_datetime}\n')
    finally:
        reaction_times = []
        with open('GameScores/ReactionTimes.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                reaction_times.append(line.split('|')[0][:-3].strip())
        return ''


@app.route("/")
def homepage_visited():
    log_visit("visited homepage")
    return render_template("home.html", title="Home", upload_size=max_upload_size)


@app.route("/about")
def about_page_visited():
    log_visit("visited about page")
    return render_template("about.html", title="About")


@app.route("/filetypes")
def filetypes_visited():
    log_visit("visited filetypes")
    return render_template("filetypes.html", title="Filetypes")


@app.route("/yt")
def yt_page_visited():
    log_visit("visited YT")
    return render_template("yt.html", title="YouTube downloader")


@app.route("/trimmer")
def trimmer_visited():
    log_visit("visited trimmer")
    return render_template("trimmer.html", title="File Trimmer")


@app.route("/contact")
def contact_page_visited():
    log_visit("visited contact page")
    return render_template("contact.html", title="Contact")


@app.route("/game")
def game_visited():
    log_visit("visited game")
    return render_template("game.html", title="Game")


@app.route("/game2")
def game2_visited():
    log_visit("visited game 2")
    return render_template("game2.html", title="Game 2")


@app.route("/chat")
def chat():
    log_visit("visited chat")
    return render_template("chat.html", title="Chat")

    
# Users online counter for /chat
count = 0


@socketio.on('connect')
def connect():
    global count
    count += 1
    socketio.emit('user connected', count)


@socketio.on('disconnect')
def disconnect():
    global count
    count -= 1
    socketio.emit('user disconnected', count)


@socketio.on('typing')
def show_typing(username):
    socketio.emit('show typing', username)


@socketio.on('nottyping')
def show_typing():
    socketio.emit('show stopped typing')


@socketio.on('message sent')
def handle_message(message):
    socketio.emit('show message', message)


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')
