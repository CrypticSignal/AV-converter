from flask import Flask, Blueprint, request, send_from_directory, jsonify, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from youtube_dl import YoutubeDL
from threading import Thread
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from time import time, sleep
import os
from loggers import log, get_ip, log_this, log_downloads_per_day

yt = Blueprint('yt', __name__)
app = Flask(__name__)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# This function runs in a separate thread.
def delete_downloads():
    while not is_downloading:
        # Give users 10 minutes to manually start the download (if necessary) before emptying the downloads folder.
        sleep(600)
        for file in os.listdir('downloads'):
            if os.path.splitext(file) != '.part':
                os.remove(os.path.join('downloads', file))
        for file in os.listdir('yt-progress'):
            os.remove(os.path.join('yt-progress', file))


def update_database():
    # Use the get_ip function imported from loggers.py
    user_ip = get_ip()
    # Query the database by IP.
    user = User.query.filter_by(ip=user_ip).first()
    if user:
        x = 'times' if user.times_used_yt_downloader == 1 else 'times'
        log.info(f'This user has used the downloader {user.times_used_yt_downloader} {x} before.')
        user.times_used_yt_downloader += 1
        db.session.commit()
    else:
        new_user = User(ip=user_ip, times_used_yt_downloader=1, mb_downloaded=0)
        db.session.add(new_user)
        db.session.commit()


def run_youtube_dl(video_link, options):
    is_downloading = True
    download_start_time = time()
    try:
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_link, download=False)
            global filename
            log.info(filename)
            # Remove the file extension and the 'downloads/' at the start.
            filename = os.path.splitext(ydl.prepare_filename(info))[0][10:]
            ydl.download([video_link])
    except KeyError:
        pass
    except Exception as error:
        log.error(f'Error downloading file:\n{error}')
        session['youtube_dl_error'] = str(error)
    else:
        download_complete_time = time()
        log.info(f'Download took {round((download_complete_time - download_start_time), 1)}s')
        log_downloads_per_day()
    finally:
        is_downloading = False

        
def send_json_response(download_type):
    global filename
    filename = [file for file in os.listdir(download_dir) if os.path.splitext(file)[0] == filename][0]
    log.info(filename)
    filesize = round((os.path.getsize(os.path.join(download_dir, filename)) / 1_000_000), 2)
    # Query the database by IP.
    user = User.query.filter_by(ip=get_ip()).first()
    # If the user has used the downloader before, update the database.
    if user:
        user.mb_downloaded += filesize
        db.session.commit()
    # Remove any hashtags or pecentage symbols as they cause an issue and make the filename more aesthetically pleasing.
    new_filename = filename.replace('#', '').replace(download_type, '.').replace('%', '').replace('_', ' ')
    os.replace(os.path.join(download_dir, filename), os.path.join(download_dir, new_filename))

    log.info(new_filename)
    log.info(f'{filesize} MB')

    # Update the list of videos downloaded.
    with open("logs/downloads.txt", "a") as f:
        f.write(f'\n{new_filename}')

    return jsonify(download_path=os.path.join('downloads', new_filename), 
                    log_file=session['progress_file_path'])


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
os.makedirs('yt-progress', exist_ok=True)
os.makedirs('downloads', exist_ok=True)
download_dir = 'downloads'
downloads_today = 0
is_downloading = False
delete_downloads_thread = Thread(target=delete_downloads)
delete_downloads_thread.daemon = True
delete_downloads_thread.start()


@yt.route("/yt", methods=["POST"])
def yt_downloader():

    # First POST request when the user clicks on a download button.
    if request.form['button_clicked'] == 'yes':
    
        log_this('Clicked on a download button.')
        update_database()
        # I want to save the download progress to a file and read from that file to show the download progress
        # to the user. Set the name of the file to the time since the epoch.
        progress_file_name = f'{str(time())[:-8]}.txt'
        session['progress_file_path'] = os.path.join('yt-progress', progress_file_name)
        return session['progress_file_path']

    # Second POST request:

    video_link = request.form['link']

    # Video (best quality)   
    if request.form['button_clicked'] == 'Video [best]':

        log.info(f'{video_link} | Video')
        options = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{download_dir}/%(title)s-[video].%(ext)s',
            'restrictfilenames': True,
            'logger': Logger()
        }
        run_youtube_dl(video_link, options)
        return send_json_response('-[video].')
       
    # MP4
    elif request.form['button_clicked'] == 'Video [MP4]':

        log.info(f'{video_link} | MP4')
        options = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{download_dir}/%(title)s-[MP4].%(ext)s',
            'restrictfilenames': True,
            'logger': Logger()
        }
        run_youtube_dl(video_link, options)
        return send_json_response('-[MP4].')

    # Audio (best quality)
    elif request.form['button_clicked'] == 'Audio [best]':

        log.info(f'{video_link} | Audio')
        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_dir}/%(title)s-[audio].%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio'
            }],
            'restrictfilenames': True,
            'logger': Logger()
        }
        run_youtube_dl(video_link, options)
        return send_json_response('-[audio].')
     
    # MP3
    elif request.form['button_clicked'] == 'MP3':

        log.info(f'{video_link} | MP3')
        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_dir}/%(title)s-[MP3].%(ext)s',
            'writethumbnail': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0' # -q:a 0
                },
                {
                    'key': 'EmbedThumbnail'
                }
            ],
            'restrictfilenames': True,
            'logger': Logger()
        }
        run_youtube_dl(video_link, options)
        return send_json_response('-[MP3].')


# This is where the youtube-dl progress file is.
@yt.route("/yt-progress/<filename>")
def get_file(filename):
    return send_from_directory('yt-progress', filename)


# This page is visited (with virtualDownloadLink.click() in app.js) to send the file to the user.
@yt.route("/downloads/<filename>", methods=["GET"])
def send_file(filename):
    time_now = datetime.now().strftime('%H:%M:%S')
    log.info(f'[{time_now}] https://free-av-tools.com/downloads/{filename}')
    mimetype_value = 'audio/mp4' if os.path.splitext(filename)[1] == ".m4a" else ''
    try:
        return send_from_directory(download_dir, filename, mimetype=mimetype_value, as_attachment=True)
    except Exception as error:
        log.error(f'Unable to send file. Error: \n{error}')

@yt.app_errorhandler(500)
def error_handler(error):
    return session['youtube_dl_error'], 500

@yt.app_errorhandler(404)
def error_handler_2(error):
    return session['youtube_dl_error']
    