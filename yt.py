from flask import Blueprint, request, send_from_directory
from urllib.parse import urlparse, parse_qs
import converter
from werkzeug.utils import secure_filename
import time
import urllib 
import shutil, os, subprocess
from loggers import log_this, log

yt = Blueprint('yt', __name__)

os.makedirs('static/yt-progress', exist_ok=True)
os.makedirs('downloads', exist_ok=True)    
download_dir = './downloads'

relevant_extensions = ["mp4", "webm", "opus", "mkv", "m4a", "ogg", "mp3"]
strings_not_allowed = ['command', ';', '$', '&&', '\\' '"', '*', '<', '>', '|', '`']
youtube_dl = 'python3 -m youtube_dl'

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

def return_download_link(video_id):
    for file in os.listdir(download_dir):
        #log.info('IN OSLISTDIR')
        if file.split('.')[-1] in relevant_extensions and video_id in file:
            log.info(f'DOWNLOADED "{file}"')
            filesize = round((os.path.getsize(f'{download_dir}/{file}') / 1_000_000), 2)
            log.info(f'{filesize} MB')
            with open("downloaded-files.txt", "a") as f:
                f.write(f'\n{file}') 
            new_filename = file.replace(f'-{video_id}', '') # Removes the video ID from the filename.
            log.info(f'NEW FILENAME: {new_filename}')

            # Without the if-statement, when running locally on Windows, the os.rename line causes an error saying
            # that the file already exists (if you try downloading the same video again). Interestingly, I don't get
            # this error on my Raspberry Pi 4 (running Raspberry Pi OS) when downloading the same video again.
            if not os.path.isfile(f'{download_dir}/{new_filename}'):
                os.rename(f'{download_dir}/{file}', f'{download_dir}/{new_filename}')
                
            if '#' in file: # Links containing a # result in a 404 error.
                os.rename(new_filename, new_filename.replace('#', ''))
    
            return f'/downloads/{new_filename}'

@yt.route("/yt", methods=["POST"])
def yt_downloader():
    progress_filename = str(time.time())[:-8]
    path_to_progress_file = f'static/yt-progress/{progress_filename}.txt'

    if request.form['button_clicked'] == 'yes':

        log_this('Clicked a button.')
        link = request.form['link']

        if converter.does_variable_contain_bad_string(link, strings_not_allowed):
            log.info('Bad string detected.')
            return 'You tried being clever, but there is a server-side check for disallowed strings.', 400

        else:
            # Create the progress file.
            with open(path_to_progress_file, "w"): pass
            log.info(f'Progress will be saved to: {path_to_progress_file}')
            return progress_filename

    # The rest runs after the 2nd POST request:

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
    download_template = f'{download_dir}/%(title)s-%(id)s.%(ext)s'
    video_id = get_video_id(link)

    if request.form['button_clicked'] == 'Video [best]':

        log.info(f'Video [best] was chosen. {link}')
        download_start_time = time.time()
        os.system(f'{youtube_dl} -o "{download_template}" --newline {video_id} > {path_to_progress_file}')
        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(video_id)
        return download_link

    elif request.form['button_clicked'] == 'Video [MP4]':

        log.info(f'MP4 was chosen. {link}')
        download_start_time = time.time()
        os.system(f'{youtube_dl} -o "{download_template}" --embed-thumbnail --newline -f '
        f'"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" {video_id} > {path_to_progress_file}')
        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(video_id)
        return download_link

    elif request.form['button_clicked'] == 'Audio [best]':

        log.info(f'Audio [best] was chosen. {link}')
        download_start_time = time.time()
        #subprocess.run(['youtube-dl', '-o', f'"{download_template}"', '--newline', '-x', '|', 'tee', path_to_progress_file], shell=False)
        os.system(f'{youtube_dl} -o "{download_template}" --newline -x {video_id} > {path_to_progress_file}')
        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(video_id)
        return download_link

    elif request.form['button_clicked'] == 'MP3':

        log.info(f'MP3 was chosen. {link}')
        download_start_time = time.time()
        os.system(f'{youtube_dl} -o "{download_template}" --newline -x --embed-thumbnail --audio-format mp3 '
        f'--audio-quality 0 {video_id} > {path_to_progress_file}')
        download_complete_time = time.time()
        log.info(f'Download took: {round((download_complete_time - download_start_time), 1)}s')
        download_link = return_download_link(video_id)
        return download_link

# Send the converted/trimmed file to the following URL, where <filename> is the "value" for downloadFilePath
@yt.route("/downloads/<filename>", methods=["GET"])
def send_file(filename):
    just_extension = filename.split('.')[-1]
    if just_extension == "m4a":
        log.info(f'freeaudioconverter.net/downloads/{filename}')
        return send_from_directory(f'{os.getcwd()}/downloads', filename, mimetype="audio/mp4", as_attachment=True)
    else:
        log.info(f'freeaudioconverter.net/downloads/{filename}')
        return send_from_directory(f'{os.getcwd()}/downloads', filename, as_attachment=True)