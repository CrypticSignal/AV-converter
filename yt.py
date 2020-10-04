from flask import Flask, Blueprint, request, send_from_directory, session, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse, parse_qs
from datetime import datetime
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
youtube_dl_path = '/usr/local/bin/youtube-dl'

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


def update_database():
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


# Function from https://gist.github.com/kmonsoor/2a1afba4ee127cce50a
def get_video_id(url):
    if url.startswith(('youtu', 'www')):
        url = 'http://' + url

    query = urlparse(url)

    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return str(parse_qs(query.query)['v'][0])
        elif query.path.startswith(('/embed/', '/v/')):
            return str(query.path.split('/')[2])
    elif 'youtu.be' in query.hostname:
        return str(query.path[1:])
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
    log.info(f'Download took {round((download_complete_time - download_start_time), 1)}s')


# Initialise the downloads_today variable.
downloads_today = 0


def log_downloads_per_day():
    # Create the file that will contain the downloads per day, if it doesn't already exist.
    if not os.path.exists('logs/downloads-per-day.txt'):
        open('logs/downloads-per-day.txt', 'x').close()

    file_contents = open('logs/downloads-per-day.txt', 'r').readlines()

    if file_contents and file_contents[0] == '\n':
        file_contents.pop(0)

    # The keys will be the date and the values will be the number of downloads.
    dates_to_downloads = {}

    for line in file_contents:
        date, downloads = line.split(' --> ')[0], line.split(' --> ')[1]
        dates_to_downloads[date] = downloads

    date_today = datetime.today().strftime('%d-%m-%Y')
    

    if date_today in dates_to_downloads:
        global downloads_today
        downloads_today += 1
        dates_to_downloads[date_today] = downloads_today
        # Use the dictionary to create a string in the format: date --> downloads
        contents_for_file = ''.join([f'{key} --> {value}' for key, value in dates_to_downloads.items()])
        # Write the string to downloads-per-day.txt
        with open('logs/downloads-per-day.txt', 'w') as f:
            f.write(contents_for_file)
    else:
        downloads_today = 1
        with open('logs/downloads-per-day.txt', 'a') as f:
            f.write(f'\n{date_today} --> {downloads_today}')


def clean_downloads_foider():
    unwanted_extensions = ['.webp', '.jpg', '.ytdl', '.part']
    for file in os.listdir(download_dir):
        if os.path.splitext(file)[1] in unwanted_extensions:
            os.remove(os.path.join(download_dir, file))


def send_json_response(progress_file_path, video_id, download_type):
    clean_downloads_foider()
    downloads = os.listdir(download_dir)
    correct_file = [filename for filename in downloads if video_id in filename and download_type in filename][0]
    log.info(f'Filename: {correct_file}')
    filesize = round((os.path.getsize(os.path.join(download_dir, correct_file)) / 1_000_000), 2)

    user_ip = get_ip()
    # Query the database by IP.
    user = User.query.filter_by(ip=user_ip).first()

    if user:
        user.mb_downloaded += filesize
        db.session.commit()

    new_filename = correct_file.replace('_', ' ').replace('#', '').replace(f'-{video_id}', '')
    os.replace(os.path.join(download_dir, correct_file), os.path.join(download_dir, new_filename))
    log.info(f'New Filename: {new_filename}')
    log.info(f'{filesize} MB')

    with open("logs/downloads.txt", "a") as f:
        f.write(f'\n{new_filename}')

    try:
        return jsonify(download_path=os.path.join('downloads', new_filename), 
                       log_file=progress_file_path)
    except Exception as error:
        log.error(f'Unable to return download and/or log file path. Error:\n{error}')


# When POST requests are made to /yt
@yt.route("/yt", methods=["POST"])
def yt_downloader():

    # First POST request when the user clicks on a download button.
    if request.form['button_clicked'] == 'yes':

        downloads_folder_size = 0

        for file in os.listdir(download_dir):
            # Downloads folder size in MB.
            downloads_folder_size += os.path.getsize(os.path.join(download_dir, file)) / 1_000_000

        if downloads_folder_size > 3000:
            log.info('Downloads folder larger than 3 GB. Emptying the folder...')
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

        return session['progress_file_path']

    # Second POST request:

    video_link = request.form['link']
    # Use the get_video_id function to get the video ID from the link.
    video_id = get_video_id(video_link)

    # Video [best]   
    if request.form['button_clicked'] == 'Video [best]':

        log_this('Chose Video [best]')
        update_database()
        log.info(f'{video_link} | {video_id}')
        download_template = f'{download_dir}/%(title)s-%(id)s [video].%(ext)s'

        args = [youtube_dl_path, '--newline', '--restrict-filenames', '--cookies', 'cookies.txt',
                '-o', download_template, '--', video_id]

        run_youtube_dl(request.form['button_clicked'], args)
        log_downloads_per_day()
        return send_json_response(session['progress_file_path'], video_id, ' [video].')
       
    # Video [MP4]
    elif request.form['button_clicked'] == 'Video [MP4]':

        log_this('Chose Video [MP4]')
        update_database()
        log.info(f'{video_link} | {video_id}')
        download_template = f'{download_dir}/%(title)s-%(id)s [MP4].%(ext)s'

        args = [youtube_dl_path, '--newline', '--restrict-filenames', '--cookies', 'cookies.txt',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                '-o', download_template, '--', video_id]

        run_youtube_dl(request.form['button_clicked'], args)
        log_downloads_per_day()
        return send_json_response(session['progress_file_path'], video_id, ' [MP4].')

    # Audio [best]
    elif request.form['button_clicked'] == 'Audio [best]':

        log_this('Chose Audio [best]')
        update_database()
        log.info(f'{video_link} | {video_id}')
        download_template = f'{download_dir}/%(title)s-%(id)s [audio].%(ext)s'

        args = [youtube_dl_path, '--newline', '--restrict-filenames', '--cookies', 'cookies.txt', '-x',
                '-o', download_template, '--', video_id]

        run_youtube_dl(request.form['button_clicked'], args)
        log_downloads_per_day()
        return send_json_response(session['progress_file_path'], video_id, ' [audio].')
     
    # MP3
    elif request.form['button_clicked'] == 'MP3':

        log_this('Chose MP3')
        update_database()
        log.info(f'{video_link} | {video_id}')
        download_template = f'{download_dir}/%(title)s-%(id)s [MP3].%(ext)s'

        args = [youtube_dl_path, '--newline', '--restrict-filenames', '--cookies', 'cookies.txt', '-x',
                '--audio-format', 'mp3', '--audio-quality', '0', '-o', download_template, '--', video_id]

        run_youtube_dl(request.form['button_clicked'], args)
        log_downloads_per_day()
        return send_json_response(session['progress_file_path'], video_id, ' [MP3].')


# This is where the youtube-dl progress file is.
@yt.route("/yt-progress/<filename>")
def get_file(filename):
    return send_from_directory('yt-progress', filename)


# This page is visited (with virtualDownloadLink.click() in app.js) to send the file to the user.
@yt.route("/downloads/<filename>", methods=["GET"])
def send_file(filename):
    log.info(f'https://free-av-tools.com/downloads/{filename}')
    mimetype_value = 'audio/mp4' if os.path.splitext(filename)[1] == ".m4a" else ''
    try:
        return send_from_directory(download_dir, filename, mimetype=mimetype_value, as_attachment=True)
    except Exception as error:
        log.error(f'Unable to send file. Error: \n{error}')
