from flask import Flask, Blueprint, request, send_from_directory, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse, parse_qs
import shutil
import time
import os
import subprocess
from loggers import log, get_ip, log_this

yt = Blueprint('yt', __name__)
app = Flask(__name__)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model): # This class is a table in the database,
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20), unique=True, nullable=False)
    times_used_yt_downloader = db.Column(db.Integer, default=0)
    mb_downloaded = db.Column(db.Float, default=0)

    def __init__(self, ip, times_used_yt_downloader, mb_downloaded):
        self.ip = ip
        self.times_used_yt_downloader = times_used_yt_downloader
        self.mb_downloaded = mb_downloaded


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

relevant_extensions = [".mp4", ".webm", ".opus", ".mkv", ".m4a", ".ogg", ".mp3"]
os.makedirs('yt-progress', exist_ok=True)
os.makedirs('downloads', exist_ok=True)
download_dir = 'downloads'


def return_download_link(progress_file_path, video_id, applicable_extensions):
    for file in os.listdir(download_dir):
       if os.path.splitext(file)[-1] in applicable_extensions and video_id in file:

            filesize = round((os.path.getsize(f'{download_dir}/{file}') / 1_000_000), 2)
            log.info(f'{filesize} MB')

            user_ip = get_ip()
            user = User.query.filter_by(ip=user_ip).first()

            if user:
                user.mb_downloaded += filesize
                db.session.commit()

            new_filename = file.replace('_', ' ').replace('#', '').replace(f'-{video_id}', '')

            with open("logs/downloads.txt", "a") as f:
                f.write(f'\n{new_filename}')

            os.replace(f'{download_dir}/{file}', f'{download_dir}/{new_filename}')

            return {
                'download_path': os.path.join('downloads', new_filename),
                'log_file': progress_file_path
            }

# If running locally, change this to the correct path.
youtube_dl_path = '/home/h/.local/bin/youtube-dl'


# When POST requests are made to /yt
@yt.route("/yt", methods=["POST"])
def yt_downloader():

    # First POST request when the user clicks on a download button.
    if request.form['button_clicked'] == 'yes':

        log_this('clicked a download button.')

        #db.create_all()
        user_ip = get_ip()
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
        progress_file_name = f'{str(time.time())[:-8]}.txt'
        session['progress_file_path'] = os.path.join('yt-progress', progress_file_name)
        log.info(f'Progress will be saved to: {session["progress_file_path"]}')

        return session['progress_file_path']

    # Second POST request:

    link = request.form['link']
    # Use the get_video_id function to get the video ID from the link.
    video_id = str(get_video_id(link))
    log.info(f'Link: {link} | ID: {video_id}')

    if request.form['button_clicked'] == 'Video [best]':

        download_template = f'{download_dir}/%(title)s-%(id)s.%(ext)s'

        args = [youtube_dl_path, '--newline', '--restrict-filenames', '--cookies', 'cookies.txt',
                '-o', download_template, '--', video_id]

        download_start_time = time.time()

        with open(session['progress_file_path'], 'w') as f:
            subprocess.run(args, stdout=f)

        download_complete_time = time.time()
        log.info(f'Video [best] was chosen. Download took: {round((download_complete_time - download_start_time), 1)}s')
        applicable_extensions = ['.mkv', '.webm']
        download_link = return_download_link(session['progress_file_path'], video_id, applicable_extensions)
        return download_link

    elif request.form['button_clicked'] == 'Video [MP4]':

        download_template = f'{download_dir}/%(title)s-%(id)s.%(ext)s'

        args = [youtube_dl_path, '--newline', '--restrict-filenames', '--cookies', 'cookies.txt',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '-o', download_template, '--', video_id]

        download_start_time = time.time()

        with open(session['progress_file_path'], 'w') as f:
            subprocess.run(args, stdout=f)

        download_complete_time = time.time()
        log.info(f'MP4 was chosen. Download took: {round((download_complete_time - download_start_time), 1)}s')
        applicable_extensions = ['.mp4']
        download_link = return_download_link(session['progress_file_path'], video_id, applicable_extensions)
        return download_link

    elif request.form['button_clicked'] == 'Audio [best]':

        download_template = f'{download_dir}/%(title)s-%(id)s.%(ext)s'

        args = [youtube_dl_path, '--newline','--restrict-filenames', '--cookies', 'cookies.txt', '-x',
                '-o', download_template, '--', video_id]

        download_start_time = time.time()

        with open(session['progress_file_path'], 'w') as f:
            subprocess.run(args, stdout=f)

        download_complete_time = time.time()
        log.info(f'Audio [best] was chosen. Download took: {round((download_complete_time - download_start_time), 1)}s')
        applicable_extensions = ['.m4a', '.ogg', '.opus']
        download_link = return_download_link(session['progress_file_path'], video_id, applicable_extensions)
        return download_link

    elif request.form['button_clicked'] == 'MP3':

        download_template = f'{download_dir}/%(title)s-%(id)s.%(ext)s'

        args = [youtube_dl_path, '--newline', '--restrict-filenames', '--cookies', 'cookies.txt', '-x',
                '--embed-thumbnail', '--audio-format', 'mp3', '--audio-quality', '0',
                '-o', download_template, '--', video_id]

        download_start_time = time.time()

        with open(session['progress_file_path'], 'w') as f:
            subprocess.run(args, stdout=f)

        download_complete_time = time.time()
        log.info(f'MP3 was chosen. Download took: {round((download_complete_time - download_start_time), 1)}s')
        applicable_extensions = ['.mp3']
        download_link = return_download_link(session['progress_file_path'], video_id, applicable_extensions)
        return download_link


@yt.route("/yt-progress/<filename>")
def get_file(filename):
    return send_from_directory('yt-progress', filename)


@yt.route("/downloads/<filename>", methods=["GET"])
def send_file(filename):
    extension = os.path.splitext(filename)[-1]
    if extension == ".m4a":
        try:
            return send_from_directory(download_dir, filename, mimetype="audio/mp4", as_attachment=True)
        finally:
            log.info(f'"{filename}" sent successfully.')
            os.remove(f'{download_dir}/{filename}')  
    else:
        try:
            return send_from_directory(download_dir, filename, as_attachment=True)
        finally:
            log.info(f'"{filename}" sent successfully.')
            os.remove(f'{download_dir}/{filename}')
