from flask import Blueprint, request, send_from_directory
from urllib.parse import urlparse, parse_qs
import converter
from werkzeug.utils import secure_filename
import time
import urllib 
from bs4 import BeautifulSoup
import shutil, os
from loggers import log_this, log

yt = Blueprint('yt', __name__)

relevant_extensions = ["mp4", "webm", "opus", "mkv", "m4a", "ogg", "webp", "mp3"]
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
    for file in os.listdir():
        if file.split('.')[-1] in relevant_extensions and video_id in file:
            log.info(f'Downloaded {file}')
            with open("downloaded-files.txt", "a") as f:
                f.write(f'\n{file}') 
            log.info(f'freeaudioconverter.net/yt/{file}')
            return f'/yt/{file}'
    
@yt.route("/yt", methods=["POST"])
def yt_downloader():

    progress_filename = str(time.time())[:-8]
    path_to_progress_file = f'static/progress/{progress_filename}.txt'

    if request.form['button_clicked'] == 'yes':

        log_this('Clicked a button.')
        link = request.form['link']

        if converter.does_variable_contain_bad_string(link, strings_not_allowed):
            log.info('Bad string detected.')
            return 'You tried being clever, but there is a server-side check for disallowed strings.', 400

        else:
            log.info('String doesn\'t seem malicious.')
            # Create the progress file.
            with open(path_to_progress_file, "w"): pass
            # Delete the pre-existing downloads.
            for file in os.listdir():
                if file.split(".")[-1] in relevant_extensions:
                    os.remove(file)
                    log.info(f'Deleted {file}')

            return progress_filename

    log.info('2nd POST request received...')

    link = request.form['link']
    # # Getting the video title using BeautifulSoup:
    # source = urllib.request.urlopen(f'{link}').read()
    # soup = BeautifulSoup(source, features="html.parser")
    # title = (soup.title.string)[:-10] # [:-10] removes the " - YouTube" at the end.
    # title = (soup.title.string[:-10]).replace('#', '') # If using the title for the filename as # causes an issue.

    video_id = get_video_id(link)

    if request.form['button_clicked'] == 'Video [best]':

        log.info(f'Video [best] was chosen. {link}')
        os.system(f'{youtube_dl} --newline {video_id} | tee {path_to_progress_file}')
        download_link = return_download_link(video_id)
        return download_link

    elif request.form['button_clicked'] == 'Video [MP4]':

        log.info(f'MP4 was chosen. {link}')
        os.system(f'{youtube_dl} --newline -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" '
        f'{video_id} | tee {path_to_progress_file}')
        download_link = return_download_link(video_id)
        return download_link

    elif request.form['button_clicked'] == 'Audio [best]':

        log.info(f'Audio [best] was chosen. {link}')
        os.system(f'{youtube_dl} --newline -x {video_id} | tee {path_to_progress_file}')
        download_link = return_download_link(video_id)
        return download_link

    elif request.form['button_clicked'] == 'MP3':

        log.info('MP3 was chosen.')
        log.info(link)
        os.system(f'{youtube_dl} --newline -x --embed-thumbnail --audio-format mp3 --audio-quality 0 {video_id} | '
        f'tee {path_to_progress_file}')
        download_link = return_download_link(video_id)
        return download_link

# Send the converted/trimmed file to the following URL, where <filename> is the "value" for downloadFilePath
@yt.route("/yt/<filename>", methods=["GET"])
def send_file(filename):
    shutil.rmtree('static/progress')
    os.mkdir('static/progress')
    just_extension = filename.split('.')[-1]
    if just_extension == "m4a":
        log.info('[M4A] Sending the file to the user.')
        return send_from_directory(os.getcwd(), filename, mimetype="audio/mp4", as_attachment=True)
    else:
        log.info('Sending the file to the user.')
        return send_from_directory(os.getcwd(), filename, as_attachment=True)