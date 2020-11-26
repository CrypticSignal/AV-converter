from datetime import datetime
import json
import os
from time import time
from pathlib import Path

from flask import Blueprint, Flask, jsonify, request, send_from_directory, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from youtube_dl import YoutubeDL

from loggers import get_ip, log, log_downloads_per_day, log_this

yt = Blueprint('yt', __name__)
app = Flask(__name__)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

os.makedirs('yt-progress', exist_ok=True)
os.makedirs('downloads', exist_ok=True)
download_dir = 'downloads'
unwanted_filetypes = ['.part', '.jpg', '.ytdl']


def update_database():
    # Use the get_ip function imported from loggers.py
    user_ip = get_ip()
    # Query the database by IP.
    user = User.query.filter_by(ip=user_ip).first()
    if user:
        user.times_used_yt_downloader += 1
        db.session.commit()
    else:
        new_user = User(ip=user_ip, times_used_yt_downloader=1, mb_downloaded=0)
        db.session.add(new_user)
        db.session.commit()


def run_youtube_dl(video_link, options):
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(video_link, download=False)
    # Remove the file extension and the 'downloads/' at the start.
    session['filename'] = os.path.splitext(ydl.prepare_filename(info))[0][10:]
    try:
        ydl.download([video_link])
    except Exception as error:
        log.error(f'Error downloading file:\n{error}')
        session['youtube_dl_error'] = str(error)
    else:
        log_downloads_per_day()
 
def return_download_path():
    session['filename'] = [file for file in os.listdir(download_dir) if Path(file).suffix not in unwanted_filetypes and 
                           os.path.splitext(file)[0] == session['filename']][0]

    filesize = round((os.path.getsize(os.path.join(download_dir, session['filename'])) / 1_000_000), 2)
    log.info(f'{session["filename"]} | {filesize} MB')

    # Query the database by IP.
    user = User.query.filter_by(ip=get_ip()).first()
    # If the user has used the downloader before, update the database.
    if user:
        user.mb_downloaded += filesize
        db.session.commit()

    # Remove any hashtags or pecentage symbols as they cause an issue and make the filename more aesthetically pleasing.
    session['new_filename'] = session['filename'].replace('#', '').replace('%', '').replace('_', ' ')
    # Rename the file.
    os.replace(os.path.join(download_dir, session['filename']), os.path.join(download_dir, session['new_filename']))

    # Update the list of videos downloaded.
    with open("logs/downloads.txt", "a") as f:
        f.write(f'\n{session["new_filename"]}')
    
    return os.path.join('downloads', session['new_filename'])


def clean_up():
    for file in os.listdir(download_dir):
        if Path(file).suffix in unwanted_filetypes:
            os.remove(f'{download_dir}/{file}')
    os.remove(f'downloads/{session["new_filename"]}')


# This value for the 'logger' key in the youtube-dl options dictionaries will be set to this class.        
class Logger():
    def debug(self, msg):
        with open(session['progress_file_path'], 'a') as f:
            f.write(msg)
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


@yt.route("/yt", methods=["POST"])
def yt_downloader():
    # First POST request when the user clicks on a download button.
    if request.form['button_clicked'] == 'yes':
        log_this(f'Chose {request.form["which_button"]}')
        update_database()
        # I want to save the download progress to a file and read from that file to show the download progress
        # to the user. Set the name of the file to the time since the epoch.
        progress_file_name = f'{str(time())[:-8]}.txt'
        session['progress_file_path'] = os.path.join('yt-progress', progress_file_name)
        return session['progress_file_path'], 200

    # Second POST request:

    video_link = request.form['link']
    log.info(video_link)

    # If the user clicked on the "Other" button.
    if request.form['button_clicked'] == 'other':
        video_audio_streams = []
        
        options = {}
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_link, download=False)
       
        for data in info['formats']:
            if data['filesize'] is not None:
                filesize = f"{round(int(data['filesize']) / 1000000, 1)} MB"
            if data['height'] is None:
                stream_type = 'Audio'
                resolution = 'N/A'
                codec = 'AAC' if 'mp4a' in data['acodec'] else data['acodec']
                extension = '.weba' if data['ext'] == 'webm' else f".{data['ext']}"
            else:
                stream_type = 'Video'
                resolution = f"{data['height']}x{data['width']}"
                if 'avc' in data['vcodec']:
                    codec = 'H.264'
                elif 'av01' in data['vcodec']:
                    codec = 'AV1'
                elif data['vcodec'] == 'vp9':
                    codec = 'VP9'
                else:
                    codec = data['vcodec']
                extension = f".{data['ext']}"

            video_audio_streams.append({
                'type': stream_type,
                'resolution': resolution,
                'codec': codec,
                'extension': extension,
                'filesize': filesize,
                'video_url': data['url']
            })

        video_audio_streams = json.dumps(video_audio_streams[::-1])
        return jsonify(streams=video_audio_streams)

    # Video (best quality)   
    elif request.form['button_clicked'] == 'Video [best]':
        options = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
            'restrictfilenames': True,
            'logger': Logger()
        }
        run_youtube_dl(video_link, options)
        return return_download_path()
       
    # MP4
    elif request.form['button_clicked'] == 'Video [MP4]':
        options = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
            'restrictfilenames': True,
            'logger': Logger()
        }
        run_youtube_dl(video_link, options)
        return return_download_path()

    # Audio (best quality)
    elif request.form['button_clicked'] == 'Audio [best]':
        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio'
            }],
            'restrictfilenames': True,
            'logger': Logger()
        }
        run_youtube_dl(video_link, options)
        return return_download_path()
     
    # MP3
    elif request.form['button_clicked'] == 'download_mp3':
        if request.form['mp3_encoding_type'] == 'cbr':
            preferredquality_value = request.form['mp3_bitrate']
            log.info(f'{preferredquality_value} kbps')
        else:
            preferredquality_value = request.form['mp3_vbr_setting']
            log.info(f'-V {preferredquality_value}')

        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
            'writethumbnail': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': preferredquality_value
                },
                {
                    'key': 'EmbedThumbnail'
                }
            ],
            'restrictfilenames': True,
            'logger': Logger()
        }
        run_youtube_dl(video_link, options)
        return return_download_path()


# This is where the youtube-dl progress file is.
@yt.route("/yt-progress/<filename>")
def get_file(filename):
    return send_from_directory('yt-progress', filename)


@yt.route("/downloads/<filename>", methods=["GET"])
def send_file(filename):
    log.info(f'{datetime.now().strftime("[%H:%M:%S]")} {filename}')
    mimetype_value = 'audio/mp4' if Path(filename).suffix == ".m4a" else ''
    try:
        return send_from_directory(download_dir, filename, mimetype=mimetype_value, as_attachment=True)
    except Exception as error:
        log.error(f'Unable to send downloads/{filename}. Error: \n{error}')
    finally:
        clean_up()


@yt.app_errorhandler(500)
def error_handler(error):
    return session['youtube_dl_error'], 500
    