from flask import Flask, Blueprint, request, send_from_directory, session, jsonify, make_response
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from youtube_dl import YoutubeDL
from threading import Thread
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import shutil
from time import time, sleep
import os
import subprocess
from loggers import log, get_ip, log_this, log_downloads_per_day

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


# This function runs in a separate thread.
def delete_downloads():
    while not is_downloading:
        # Give users 10 minutes to manually start the download (if necessary) before emptying the downloads folder.
        sleep(600)
        for file in os.listdir('downloads'):
            os.remove(os.path.join('downloads', file))


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


# Slightly modified version of https://gist.github.com/kmonsoor/2a1afba4ee127cce50a0
def get_video_id(url):
    url = f'http://{url}' if url.startswith(('youtu', 'www')) else url
    query = urlparse(url)
    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith(('/embed/', '/v/')):
            return query.path.split('/')[2]
    elif 'youtu.be' in query.hostname:
        return query.path[1:]
    return None


def run_youtube_dl(video_link, options):
    is_downloading = True
    download_start_time = time()
    try:
        with YoutubeDL(options) as ydl:
            ydl.download(video_link)
    except Exception as error:
        log.error(f'Error downloading file:\n{error}')
        session['youtube_dl_error'] = str(error)
    else:
        download_complete_time = time()
        log.info(f'Download took {round((download_complete_time - download_start_time), 1)}s')
        log_downloads_per_day()
    finally:
        is_downloading = False


def clean_downloads_foider():
    unwanted_extensions = ['.webp', '.jpg', '.ytdl', '.part']
    for file in os.listdir(download_dir):
        if os.path.splitext(file)[1] in unwanted_extensions:
            os.remove(os.path.join(download_dir, file))


def send_json_response(progress_file_path, video_id, download_type):
    clean_downloads_foider()
    downloads = os.listdir(download_dir)
    correct_file = [filename for filename in downloads if video_id in filename and download_type in filename][0]
    log.info(correct_file)
    filesize = round((os.path.getsize(os.path.join(download_dir, correct_file)) / 1_000_000), 2)
    # Query the database by IP.
    user = User.query.filter_by(ip=get_ip()).first()
    # If the user has used the downloader before, update the database.
    if user:
        user.mb_downloaded += filesize
        db.session.commit()
    # Remove any hashtags or pecentage symbols as they cause an issue and make the filename more aesthetically pleasing.
    new_filename = correct_file.replace('#', '').replace(f'-{video_id}{download_type}', '').replace('%', '').replace('_', ' ')
    log.info(new_filename)
    os.replace(os.path.join(download_dir, correct_file), os.path.join(download_dir, new_filename))
    # Update the list of videos downloaded.
    with open("logs/downloads.txt", "a") as f:
        f.write(f'\n{new_filename}')

    return jsonify(download_path=os.path.join('downloads', new_filename), 
                    log_file=progress_file_path)
 
        
class Logger():
    def debug(self, msg):
        with open(session['progress_file_path'], 'a') as f:
            f.write(msg)
    def warning(self, msg):
        pass
    def error(self, msg):
        pass

# youtube-dl options template dictionary.
options = {
    # Prevent "'latin-1' codec can't encode characters in position 18-23: ordinal not in range(256)" error.
    'restrictfilenames': True,
    # Set the value of the logger key to the logger class created above.
    'logger': Logger()
}

# Initialization
db.create_all()
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
    video_id = video_link.split('=')[1] if get_video_id(video_link) is None else get_video_id(video_link)

    # Video [best]   
    if request.form['button_clicked'] == 'Video [best]':
        log.info(f'{video_link} | Video')
        options['format'] = 'bestvideo+bestaudio/best'
        options['outtmpl'] = f'{download_dir}/%(title)s-%(id)s-[video].%(ext)s'
        run_youtube_dl([video_link], options)
        return send_json_response(session['progress_file_path'], video_id, '-[video]')
       
    # Video [MP4]
    elif request.form['button_clicked'] == 'Video [MP4]':

        log.info(f'{video_link} | MP4')
        options['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        options['outtmpl'] = f'{download_dir}/%(title)s-%(id)s-[MP4].%(ext)s'
        run_youtube_dl([video_link], options)
        return send_json_response(session['progress_file_path'], video_id, '-[MP4]')

    # Audio [best]
    elif request.form['button_clicked'] == 'Audio [best]':

        log.info(f'{video_link} | Audio')
        options['format'] = 'bestaudio'
        options['outtmpl'] = f'{download_dir}/%(title)s-%(id)s-[audio].%(ext)s'
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio'
        }]
        run_youtube_dl([video_link], options)
        return send_json_response(session['progress_file_path'], video_id, '-[audio]')
     
    # MP3
    elif request.form['button_clicked'] == 'MP3':

        log.info(f'{video_link} | MP3')
        options['format'] = 'bestaudio'
        options['audioformat'] = 'mp3'
        options['outtmpl'] = f'{download_dir}/%(title)s-%(id)s-[MP3].%(ext)s'
        options['writethumbnail'] = True
        options['postprocessors'] = [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0' # -q:a 0
            },
            {
                'key': 'EmbedThumbnail'
            }
        ]
        run_youtube_dl([video_link], options)
        return send_json_response(session['progress_file_path'], video_id, '-[MP3]')


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
    return f"[youtube-dl error] {session['youtube_dl_error']}", 500
    