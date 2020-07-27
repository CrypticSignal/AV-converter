from flask import Flask, Blueprint, request, send_from_directory, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse, parse_qs
import time
import os, subprocess
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

os.makedirs('yt-progress', exist_ok=True)
os.makedirs('downloads', exist_ok=True)
download_dir = 'downloads'

# If running locally, change this to the correct path.
youtube_dl_path = '/home/h/.local/bin/youtube-dl'

relevant_extensions = ["mp4", "webm", "opus", "mkv", "m4a", "ogg", "mp3"]

def get_video_id(url): # Function from https://gist.github.com/kmonsoor/2a1afba4ee127cce50a
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


def return_download_link(progress_file_path, video_id, download_type):
    for file in os.listdir(download_dir):
        if file.split('.')[-1] in relevant_extensions and video_id in file and download_type in file:

            log.info(f'DOWNLOADED "{file}"')
            filesize = round((os.path.getsize(f'{download_dir}/{file}') / 1_000_000), 2)
            log.info(f'{filesize} MB')

            user_ip = get_ip()
            user = User.query.filter_by(ip=user_ip).first()

            if user:
                user.mb_downloaded += filesize
                db.session.commit()

            with open("logs/downloaded-files.txt", "a") as f:
                f.write(f'\n{file}')

            new_filename = file.replace('#', '').replace(f'-{video_id}', '')
            os.replace(f'{download_dir}/{file}', f'{download_dir}/{new_filename}')

            return {
                'download_path': os.path.join('downloads', new_filename),
                'log_file': progress_file_path
            }


# When POST requests are made to /yt
@yt.route("/yt", methods=["POST"])
def yt_downloader():

    if request.form['button_clicked'] == 'yes':

        log_this('Clicked a download button.')
        #db.create_all()

        # Intialise the size_of_media_files variable
        size_of_media_files = 0
        # Iterate over each file in the folder and add its size to the above variable.
        for file in os.listdir(download_dir):
            size_of_file = os.path.getsize(f'{download_dir}/{file}') / 1_000_000
            size_of_media_files += size_of_file
        # If there's more than 10 GB of files in the downloads folder, empty it.
        if size_of_media_files > 10_000:
            log.info(f'More than 10 GB worth of downloads found. Emptying downloads folder...')
            for file in os.listdir(download_dir):
                if file.split('.')[-1] in relevant_extensions:
                    os.remove(f'{download_dir}/{file}')
            log.info('Downloads folder emptied.')

        # I want to save the download progress to a file and read from that file to show the download progress
        # to the user. Set the name of the file to the time since the epoch.
        progress_file_name = str(time.time())[:-8] + '.txt'
        session['progress_file_path'] = os.path.join('yt-progress', progress_file_name)
        log.info(f'Progress will be saved to: {session["progress_file_path"] }')

        user_ip = request.environ['REMOTE_ADDR']
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

        return session['progress_file_path']

    # The following runs after the 2nd POST request:

    link = request.form['link']
    video_id = str(get_video_id(link))
    log.info(f'LINK: {link} | ID: {video_id}')

    if request.form['button_clicked'] == 'Video [best]':

        log.info(f'Video [best] was chosen.')
        download_template = f'{download_dir}/%(title)s-%(id)s [Video].%(ext)s'

        args = [youtube_dl_path, '--restrict-filenames', '--cookies', 'cookies.txt',
                '-o', download_template, '--newline', '--', video_id]

        download_start_time = time.time()

        with open(session['progress_file_path'], 'w') as f:
            subprocess.run(args, stdout=f)

        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(session['progress_file_path'], video_id, '[Video]')
        return download_link

    elif request.form['button_clicked'] == 'Video [MP4]':

        log.info(f'MP4 was chosen.')
        download_template = f'{download_dir}/%(title)s-%(id)s [MP4].%(ext)s'

        args = [youtube_dl_path, '--restrict-filenames', '--cookies', 'cookies.txt', '-o', download_template,
                '--newline', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '--', video_id]

        download_start_time = time.time()

        with open(session['progress_file_path'], 'w') as f:
            subprocess.run(args, stdout=f)

        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(session['progress_file_path'], video_id, '[MP4]')
        return download_link

    elif request.form['button_clicked'] == 'Audio [best]':

        log.info(f'Audio [best] was chosen.')
        download_template = f'{download_dir}/%(title)s-%(id)s [Audio].%(ext)s'

        args = [youtube_dl_path, '-x', '--restrict-filenames', '--cookies', 'cookies.txt',
                '-o', download_template, '--newline', '--', video_id]

        download_start_time = time.time()

        with open(session['progress_file_path'], 'w') as f:
            subprocess.run(args, stdout=f)

        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(session['progress_file_path'], video_id, '[Audio]')
        return download_link

    elif request.form['button_clicked'] == 'MP3':

        log.info(f'MP3 was chosen.')
        download_template = f'{download_dir}/%(title)s-%(id)s [MP3].%(ext)s'

        args = [youtube_dl_path, '-x', '--restrict-filenames', '--cookies', 'cookies.txt', '-id3v2_version', '3',
                '--embed-thumbnail', '-o', download_template, '--newline', '--audio-format', 'mp3',
                '--audio-quality', '0', '--', video_id]

        download_start_time = time.time()

        with open(session['progress_file_path'], 'w') as f:
            subprocess.run(args, stdout=f)

        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(session['progress_file_path'], video_id, '[MP3]')
        return download_link


@yt.route("/yt-progress/<filename>")
def get_file(filename):
    return send_from_directory('yt-progress', filename)


@yt.route("/downloads/<filename>", methods=["GET"])
def send_file(filename):
    extension = os.path.splitext(filename)[-1]
    if extension == ".m4a":
        log.info(f'https://free-av-tools.com/downloads/{filename}')
        return send_from_directory('downloads', filename, mimetype="audio/mp4", as_attachment=True)
    else:
        log.info(f'https://free-av-tools.com/downloads/{filename}')
        return send_from_directory('downloads', filename, as_attachment=True)