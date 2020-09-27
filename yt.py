from flask import Flask, Blueprint, request, send_from_directory, session, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse, parse_qs
import shutil
from time import time
import os
import subprocess
from loggers import log, get_ip, log_this

yt = Blueprint('yt', __name__)
app = Flask(__name__)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

# If running locally, change this to the correct path.
youtube_dl_path = '/home/h/.local/bin/youtube-dl'

# Create the necessary folders and define the directory to save the downloads to.
os.makedirs('yt-progress', exist_ok=True)
os.makedirs('downloads', exist_ok=True)
download_dir = 'downloads'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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

db.create_all()


# Function from https://gist.github.com/kmonsoor/2a1afba4ee127cce50a
def get_video_id(url):
    if url.startswith(('youtu', 'www')):
        url = 'http://' + url

    query = urlparse(url)

    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith(('/embed/', '/v/')):
            return query.path.split('/')[2]
    elif 'youtu.be' in query.hostname:
        return query.path[1:]
    else:
        raise ValueError


def run_youtube_dl(download_type, args):
    download_start_time = time()
    try:
        # Using subprocess.run() this way allows the stdout to be written to a file.
        with open(session['progress_file_path'], 'w') as f:
            subprocess.run(args, stdout=f)
    except Exception as error:
        log.error(f'Unable to download video: \n{error}')

    download_complete_time = time()
    log.info(f'{download_type} was chosen. Download took: {round((download_complete_time - download_start_time), 1)}s')

# This list is used in the function below.
unwanted_extensions = ['.webp', '.jpg']

# This function returns a JSON response containing the relative path of the file that needs to be sent to the user, 
# and the relative path of the youtube-dl log file.
def send_json_response(progress_file_path, video_id):
    for file in os.listdir(download_dir):
        
        if video_id in file and not os.path.splitext(file)[0].endswith('.temp') \
            and os.path.splitext(file)[1] not in unwanted_extensions:

            filesize = round((os.path.getsize(os.path.join(download_dir, file)) / 1_000_000), 2)
            log.info(f'{filesize} MB')

            user_ip = get_ip()
            # Query the database by IP.
            user = User.query.filter_by(ip=user_ip).first()

            if user:
                user.mb_downloaded += filesize
                db.session.commit()

            new_filename = file.replace('_', ' ').replace('#', '').replace(f'-{video_id}', '')
            log.info(new_filename)
            os.replace(os.path.join(download_dir, file), os.path.join(download_dir, new_filename))

            with open("logs/downloads.txt", "a") as f:
                f.write(f'\n{new_filename}')

            return jsonify(download_path=os.path.join('downloads', new_filename), 
                           log_file=progress_file_path)


# When POST requests are made to /yt
@yt.route("/yt", methods=["POST"])
def yt_downloader():

    # First POST request when the user clicks on a download button.
    if request.form['button_clicked'] == 'yes':

        log_this('clicked a download button.')

        downloads_folder_size = 0

        for file in os.listdir(download_dir):
            # Downloads folder size in MB.
            downloads_folder_size += os.path.getsize(os.path.join(download_dir, file)) / 1_000_000

        if downloads_folder_size > 1000:
            log.info('Downloads folder larger than 1 GB. Emptying the folder...')
            for file in os.listdir(download_dir):
                os.remove(os.path.join(download_dir, file))
            log.info('Downloads folder emptied.')
        
        # Use the get_ip function imported from loggers.py
        user_ip = get_ip()
        # Query the database by IP.
        user = User.query.filter_by(ip=user_ip).first()

        if user:
            x = 'time' if user.times_used_yt_downloader == 1 else 'times'
            log.info(f'This user has used the downloader {user.times_used_yt_downloader} {x} before.')
            user.times_used_yt_downloader += 1
            db.session.commit()
        else:
            new_user = User(ip=user_ip, times_used_yt_downloader=1, mb_downloaded=0)
            db.session.add(new_user)
            db.session.commit()

        # I want to save the download progress to a file and read from that file to show the download progress
        # to the user. Set the name of the file to the time since the epoch.
        progress_file_name = f'{str(time())[:-8]}.txt'
        session['progress_file_path'] = os.path.join('yt-progress', progress_file_name)
        log.info(f'Progress will be saved to: {session["progress_file_path"]}')

        return session['progress_file_path']

    # Second POST request:

    video_link = request.form['link']
    # Use the get_video_id function to get the video ID from the link.
    video_id = str(get_video_id(video_link))
    log.info(f'{video_link} | {video_id}')

    download_template = f'{download_dir}/%(title)s-%(id)s.%(ext)s'

    # Video [best]   
    if request.form['button_clicked'] == 'Video [best]':

        args = [youtube_dl_path, '--newline', '--restrict-filenames', '--cookies', 'cookies.txt',
                '-o', download_template, '--', video_id]

        run_youtube_dl(request.form['button_clicked'], args)
        return send_json_response(session['progress_file_path'], video_id)
       
    # Video [MP4]
    elif request.form['button_clicked'] == 'Video [MP4]':

        args = [youtube_dl_path, '--newline', '--restrict-filenames', '--cookies', 'cookies.txt',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '-o', download_template, '--', video_id]

        run_youtube_dl(request.form['button_clicked'], args)
        return send_json_response(session['progress_file_path'], video_id)

    # Audio [best]
    elif request.form['button_clicked'] == 'Audio [best]':

        args = [youtube_dl_path, '--newline','--restrict-filenames', '--cookies', 'cookies.txt', '-x',
                '-o', download_template, '--', video_id]

        run_youtube_dl(request.form['button_clicked'], args)
        return send_json_response(session['progress_file_path'], video_id)
     
    # MP3
    elif request.form['button_clicked'] == 'MP3':

        args = [youtube_dl_path, '--newline', '--restrict-filenames', '--cookies', 'cookies.txt', '-x',
                '--embed-thumbnail', '--audio-format', 'mp3', '--audio-quality', '0',
                '-o', download_template, '--', video_id]

        run_youtube_dl(request.form['button_clicked'], args)
        return send_json_response(session['progress_file_path'], video_id)


# This is where the youtube-dl progress file is.
@yt.route("/yt-progress/<filename>")
def get_file(filename):
    return send_from_directory('yt-progress', filename)


# This page is visited (with virtualDownloadLink.click() in app.js) to send the file to the user.
@yt.route("/downloads/<filename>", methods=["GET"])
def send_file(filename):
    log.info(f'https://free-av-tools.com/downloads/{filename}')
    if os.path.splitext(filename)[1] == ".m4a":
        try:
            return send_from_directory(download_dir, filename, mimetype="audio/mp4", as_attachment=True)
        except Exception as error:
            log.error(f'Unable to send file. Error: \n{error}')
    else:
        try:
            return send_from_directory(download_dir, filename, as_attachment=True)
        except Exception as error:
            log.error(f'Unable to send file. Error: \n{error}')
