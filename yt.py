from flask import Flask, Blueprint, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse, parse_qs
from werkzeug.utils import secure_filename
import time
import urllib 
import, os, subprocess
from loggers import log_this, log

yt = Blueprint('yt', __name__)

app = Flask(__name__)
db = SQLAlchemy(app)

class User(db.Model): # This class is a table in the database,
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20), unique=True, nullable=False)
    times_used_converter = db.Column(db.Integer, default=0)
    times_used_yt_downloader = db.Column(db.Integer, default=0)

    def __init__(self, ip, times_used_yt_downloader):
        self.ip = ip
        self.times_used_yt_downloader = times_used_yt_downloader

os.makedirs('static/yt-progress', exist_ok=True)
os.makedirs('downloads', exist_ok=True)    
download_dir = 'downloads'

relevant_extensions = ["mp4", "webm", "opus", "mkv", "m4a", "ogg", "mp3"]

youtube_dl_path = '/usr/local/bin/youtube-dl' # If running locally, change this to the correct path.

def get_video_id(url): # Function from https://stackoverflow.com/a/54383711/13231825
    # Examples:
    # http://youtu.be/SA2iWivDJiE
    # http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    # http://www.youtube.com/embed/SA2iWivDJiE
    # http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    query = urlparse(url)
    if query.hostname == 'youtu.be': return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]
    # Fail?
    return None

def return_download_link(progress_file, video_id, download_type):
    
    for file in os.listdir(download_dir):
        if file.split('.')[-1] in relevant_extensions and video_id in file and download_type in file:

            log.info(f'DOWNLOADED "{file}"')
            filesize = round((os.path.getsize(f'{download_dir}/{file}') / 1_000_000), 2)
            log.info(f'{filesize} MB')

            with open("downloaded-files.txt", "a") as f:
                f.write(f'\n{file}') 

            new_filename = file.replace(f'-{video_id}', '') # Remove the video ID from the filename.
            log.info(f'NEW FILENAME: {new_filename}')

            # Without this if-statement, when running locally on Windows, the os.rename line causes an error saying
            # that the file already exists (if you try downloading the same video again).
            if not os.path.isfile(f'{download_dir}/{new_filename}'):
                os.rename(f'{download_dir}/{file}', f'{download_dir}/{new_filename}')
                
            if '#' in file: # Links containing a # result in a 404 error.
                os.rename(new_filename, new_filename.replace('#', ''))

            return {
                'download_path': f'/downloads/{new_filename}',
                'log_file': progress_file
            }

@yt.route("/yt", methods=["POST"])
def yt_downloader():
    progress_filename = str(time.time())[:-8]
    path_to_progress_file = f'static/yt-progress/{progress_filename}.txt'

    if request.form['button_clicked'] == 'yes':

        log_this('Clicked a button.')
        link = request.form['link']

        # Create the progress file.
        with open(path_to_progress_file, "w"): pass
        log.info(f'Progress will be saved to: {path_to_progress_file}')
        return progress_filename

    # The following runs after the 2nd POST request:

    size_of_media_files = 0
    # Get the total size of the media files in the download folder.
    for file in os.listdir(download_dir):
        size_of_file = os.path.getsize(f'{download_dir}/{file}') / 1_000_000
        size_of_media_files += size_of_file
            
    log.info(f'SIZE OF MEDIA FILES: {round(size_of_media_files, 2)} MB')

    # If there's more than 10 GB of media files, delete them:
    if size_of_media_files > 10_000:
        log.info(f'More than 10 GB worth of media files found.')
        for file in os.listdir(download_dir):
            if file.split('.')[-1] in relevant_extensions:
                os.remove(f'{download_dir}/{file}')
                log.info(f'DELETED {file}')

    link = request.form['link']
    #download_template = f'{download_dir}/%(title)s.%(ext)s'
    video_id = get_video_id(link)

    if request.form['button_clicked'] == 'Video [best]':

        log.info(f'Video [best] was chosen. {link}')
        download_template = f'{download_dir}/%(title)s-%(id)s [Video].%(ext)s'
        download_start_time = time.time()

        with open(path_to_progress_file, 'w') as f:
            subprocess.run([youtube_dl_path, '-v', '-o', download_template, '--newline', '--', video_id], stdout=f)

        download_complete_time = time.time()

        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(path_to_progress_file, video_id, '[Video]')
        return download_link

    elif request.form['button_clicked'] == 'Video [MP4]':

        log.info(f'MP4 was chosen. {link}')
        download_template = f'{download_dir}/%(title)s-%(id)s [MP4].%(ext)s'
        download_start_time = time.time()

        with open(path_to_progress_file, 'w') as f:
            subprocess.run([youtube_dl_path, '-v', '-o', download_template, '--newline', '-f',
            'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '--', video_id], stdout=f)

        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(path_to_progress_file, video_id, '[MP4]')
        return download_link

    elif request.form['button_clicked'] == 'Audio [best]':

        log.info(f'Audio [best] was chosen. {link}')
        download_template = f'{download_dir}/%(title)s-%(id)s [Audio].%(ext)s'
        download_start_time = time.time()

        with open(path_to_progress_file, 'w') as f:
            subprocess.run([youtube_dl_path, '-v', '-o', download_template, '--newline', '-x', '--', video_id],
                stdout=f)

        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(path_to_progress_file, video_id, '[Audio]')
        return download_link

    elif request.form['button_clicked'] == 'MP3':

        log.info(f'MP3 was chosen. {link}')
        download_template = f'{download_dir}/%(title)s-%(id)s [MP3].%(ext)s'
        download_start_time = time.time()

        with open(path_to_progress_file, 'w') as f:
            subprocess.run([youtube_dl_path, '-v', '-o', download_template, '--newline', '-x',
            '--audio-format', 'mp3', '--audio-quality', '0', '--', video_id], stdout=f)

        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(path_to_progress_file, video_id, '[MP3]')
        return download_link

@yt.route("/downloads/<filename>", methods=["GET"])
def send_file(filename):
    #db.create_all()
    user_ip = request.environ['HTTP_X_FORWARDED_FOR']
    user = User.query.filter_by(ip=user_ip).first()
    log.info(user)

    if user:
        user.times_used_yt_downloader += 1
        x = 'time' if user.times_used_yt_downloader == 1 else 'times'
        log.info(f'This user has used the downloader {user.times_used_yt_downloader} {x}.')
        db.session.commit()
    else:
        new_user = User(ip=user_ip, times_used_yt_downloader=1)
        db.session.add(new_user)
        db.session.commit()

    just_extension = filename.split('.')[-1]

    if just_extension == "m4a":
        log.info(f'https://freeaudioconverter.net/downloads/{filename}')
        return send_from_directory(f'{os.getcwd()}/downloads', filename, mimetype="audio/mp4", as_attachment=True)
    else:
        log.info(f'https://freeaudioconverter.net/downloads/{filename}')
        return send_from_directory(f'{os.getcwd()}/downloads', filename, as_attachment=True)