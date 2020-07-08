from flask import Flask, request, render_template, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from yt import yt # Importing the blueprint in yt.py
from trimmer import trimmer # Importing the blueprint in trimmer.py
from loggers import log, log_this, log_visit
from werkzeug.utils import secure_filename
from time import time
from datetime import datetime
import os
import converter

app = Flask(__name__)
secret_key = str(os.urandom(16))
app.secret_key = secret_key
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

app.register_blueprint(trimmer)
app.register_blueprint(yt)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
max_upload_size = 5 # in GB.
app.config['MAX_CONTENT_LENGTH'] = max_upload_size * 1000 * 1000 * 1000 # Max upload size.
app.jinja_env.auto_reload = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model): # This class is a table in the database.

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), unique=True, nullable=False)
    times_used_converter = db.Column(db.Integer, default=0)
    times_used_yt_downloader = db.Column(db.Integer, default=0)

    def __init__(self, ip, times_used_converter):
        self.ip = ip
        self.times_used_converter = times_used_converter

# When a file has been uploaded, a POST request is sent to the homepage.
@app.route("/", methods=["POST"])
def homepage():
    if request.form['request_type'] == 'log_convert_clicked':
        log_this('clicked on the convert button.')
        return ''

    elif request.form["request_type"] == "uploaded":

        session['progress_filename'] = str(time())[:-8]
    
        log_this('uploaded a file:')
        chosen_file = request.files["chosen_file"]
        filesize = request.form["filesize"]
        log.info(chosen_file)
        log.info(f'Size: {filesize} MB')
        
        # Make the filename safe
        filename_secure = secure_filename(chosen_file.filename)
        # Save the uploaded file to the uploads folder.
        os.makedirs('uploads', exist_ok=True) 
        chosen_file.save(os.path.join("uploads", filename_secure))
        
        return session['progress_filename']
    
    elif request.form["request_type"] == "convert":

        wav_bit_depth = request.form["wav_bit_depth"]
        filename = request.form["filename"]
        chosen_codec = request.form["chosen_codec"]
        crf_value = request.form["crf_value"]
        mp4_encoding_mode = request.form["mp4_encoding_mode"]
        is_keep_video = request.form["is_keep_video"]
        uploaded_file_path = os.path.join("uploads", secure_filename(filename))
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
        # Desired filename
        output_name = request.form["output_name"]
 
        log.info(f'They chose {chosen_codec} | Output Filename: {output_name}')
        os.makedirs('conversions', exist_ok=True)
        output_path = f'conversions/{output_name}'

        # Run the appropriate section of converter.py:

        if chosen_codec == 'MP3':
            converter.run_mp3(session['progress_filename'], uploaded_file_path, is_keep_video, mp3_encoding_type,
            mp3_bitrate, mp3_vbr_setting, output_path)
            if is_keep_video == "yes":
                just_ext = uploaded_file_path.split('.')[-1]
                if just_ext == 'mp4':
                    extension = 'mp4'
                else:
                    extension = 'mkv'
            else:
                extension = 'mp3'

        elif chosen_codec == 'AAC':
            converter.run_aac(session['progress_filename'], uploaded_file_path, is_keep_video, fdk_type, fdk_cbr,
            fdk_vbr, is_fdk_lowpass,
            fdk_lowpass, output_path)
            if is_keep_video == "yes":
                just_ext = uploaded_file_path.split('.')[-1]
                if just_ext == 'mp4':
                    extension = 'mp4'
                else:
                    extension = 'mkv'
            else:
                extension = 'm4a'

        elif chosen_codec == 'Opus':
            converter.run_opus(session['progress_filename'], uploaded_file_path, opus_encoding_type, opus_vorbis_slider,
            opus_cbr_bitrate, output_path)
            extension = 'opus'   

        elif chosen_codec == 'FLAC':
            converter.run_flac(session['progress_filename'], uploaded_file_path, is_keep_video, flac_compression,
            output_path)
            if is_keep_video == "yes":
                extension = 'mkv'
            else:
                extension = 'flac'

        elif chosen_codec == 'Vorbis':
            converter.run_vorbis(session['progress_filename'], uploaded_file_path, vorbis_encoding, vorbis_quality,
            opus_vorbis_slider, output_path) 
            extension = 'mka'

        elif chosen_codec == 'WAV':
            converter.run_wav(session['progress_filename'], uploaded_file_path, is_keep_video, wav_bit_depth, output_path)
            if is_keep_video == "yes":
                extension = 'mkv'
            else:
                extension = 'wav'

        elif chosen_codec == 'MKV':
            converter.run_mkv(session['progress_filename'], uploaded_file_path, output_path)
            extension = 'mkv'

        elif chosen_codec == 'MKA':
            converter.run_mka(session['progress_filename'], uploaded_file_path, output_path)
            extension = 'mka'

        elif chosen_codec == 'ALAC':
            converter.run_alac(session['progress_filename'], uploaded_file_path, is_keep_video, output_path)
            if is_keep_video == "yes":
                extension = 'mkv'
            else:
                extension = 'm4a'

        elif chosen_codec == 'AC3':
            converter.run_ac3(session['progress_filename'], uploaded_file_path, is_keep_video, ac3_bitrate, output_path)
            if is_keep_video == "yes":
                just_ext = uploaded_file_path.split('.')[-1]
                if just_ext == 'mp4':
                    extension = 'mp4'
                else:
                    extension = 'mkv'
            else:
                extension = 'ac3'

        elif chosen_codec == 'CAF':
            converter.run_caf(session['progress_filename'], uploaded_file_path, output_path)
            extension = 'caf'

        elif chosen_codec == 'DTS':
            converter.run_dts(session['progress_filename'], uploaded_file_path, is_keep_video, dts_bitrate, output_path)
            if is_keep_video == "yes":
                extension = 'mkv'
            else:
                extension = 'dts'

        elif chosen_codec == 'MP4':
            converter.run_mp4(session['progress_filename'], uploaded_file_path, mp4_encoding_mode, crf_value, output_path)
            extension = 'mp4'
        
        elif chosen_codec == 'MKV':
            converter.run_mkv(session['progress_filename'], uploaded_file_path, output_path)
            extension = 'mkv'

        converted_file_name = output_name + "." + extension
        return f'/conversions/{converted_file_name}'

@app.route("/conversions/<filename>", methods=["GET"])
def send_file(filename):
    #db.create_all()
    user_ip = request.environ['HTTP_X_FORWARDED_FOR']
    user = User.query.filter_by(ip=user_ip).first()
    log.info(user)

    if user:
        user.times_used_converter += 1
        x = 'time' if user.times_used_converter == 1 else 'times'
        log.info(f'This user has used the converter {user.times_used_converter} {x}.')
        db.session.commit()
    else:
        new_user = User(ip=user_ip, times_used_converter=1)
        db.session.add(new_user)
        db.session.commit()

    just_extension = filename.split('.')[-1]

    if just_extension == "m4a":
        log.info(f'https://freeaudioconverter.net/conversions/{filename}')
        return send_from_directory('conversions', filename, mimetype="audio/mp4", as_attachment=True)
    else:
        log.info(f'https://freeaudioconverter.net/conversions/{filename}')
        return send_from_directory('conversions', filename, as_attachment=True)

# END OF CODE FOR AUDIO/VIDEO CONVERTER --------------------------------------------------------------------------------

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
        int(canvas_width)
    except ValueError:
        log.error("GAME 1: The user changed something to a non-int.")
    else:
        with open("Game Scores/HighScores.txt", "a") as f:
            f.write(f'{score} | {times_missed} | {user} | {user_agent} | {canvas_width}'
            f'x{canvas_height} | {current_datetime}\n')
    finally:
        just_scores = []
        with open('Game Scores/HighScores.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                just_scores.append(line.split('|')[0].strip())
        #valid_scores = [x for x in just_scores if int(x) < 100]
        #world_record = max(valid_scores, key=lambda x: int(x))
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
        log.error("GAME 2: The user changed reaction_time to a non-int.")
    else:
        with open("Game Scores/ReactionTimes.txt", "a") as f:
            f.write(f'{reaction_time} ms | {user} | {user_agent} | {current_datetime}\n')
    finally:
        reaction_times = []
        with open('Game Scores/ReactionTimes.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                reaction_times.append(line.split('|')[0][:-3].strip())
        # reaction_record = min(reaction_times, key=lambda x: int(x))
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

if __name__ == "__main__":
    app.run(host="0.0.0.0")