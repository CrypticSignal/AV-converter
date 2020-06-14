from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
import time
import urllib 
from bs4 import BeautifulSoup 
import converter
import shutil, os
from loggers import log_this, log

yt = Blueprint('yt',__name__)

def delete_progress_files():
    shutil.rmtree('static/progress')
    os.mkdir('static/progress')

@yt.route("/yt", methods=["POST"])
def yt_downloader():
    progress_filename = str(time.time())[:-8]

    if request.form['button_clicked'] == 'yes':

        with open(f'static/progress/{progress_filename}.txt', "w"): pass

        return progress_filename

    path_to_progress_file = f'static/progress/{progress_filename}.txt'

    media_extensions = ["mp4", "webm", "opus", "mkv", "aac", "m4a", "mp3"]
    strings_not_allowed = ['command', ';', '$', '&&', '\\' '"', '*', '<', '>', '|', '`']
    link = request.form['link']
    source = urllib.request.urlopen(f'{link}').read()
    soup = BeautifulSoup(source, features="html.parser")
    title = (soup.title.string[:-10]).replace('#', '')

    # check_no_variable_contains_bad_string is a func defined in converter.py
    if not converter.check_no_variable_contains_bad_string(link, strings_not_allowed):
        return {"message": "You tried being clever, but there's a server-side check for disallowed strings."}, 400
    
    # Delete the videos that have already been downloaded so send_from_directory does not send back the wrong file.
    for file in os.listdir():
        if file.split(".")[-1] in media_extensions:
            os.remove(file)
        else:
            pass

    if request.form['button_clicked'] == 'Video [best]':

        log_this('chose Video [best]')
        log.info(title)
        os.system(f'youtube-dl --newline -o "{title}" {link} | tee {path_to_progress_file}')
        log.info('DOWNLOAD COMPLETE.')
        delete_progress_files()

        with open("downloaded-files.txt", "a") as f:
            f.write("\n" + title + " downloaded.") 

        for file in os.listdir():
            if file.split(".")[-1] in media_extensions:
                return f'/yt/{file}'

    elif request.form['button_clicked'] == 'Video [MP4]':

        log_this('chose Video [MP4]')
        log.info(title)
        os.system(f'youtube-dl --newline -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "{title}" '
        f'{link} | tee {path_to_progress_file}')
        log.info('DOWNLOAD COMPLETE.')
        delete_progress_files()

        with open("downloaded-files.txt", "a") as f:
            f.write("\n" + title + " downloaded.") 
        
        for file in os.listdir():
            if file.split(".")[-1] in media_extensions:
                return f'/yt/{file}'

    elif request.form['button_clicked'] == 'Audio [best]':

        log_this('chose Audio [best]')
        log.info(title)
        os.system(f'youtube-dl --newline -x -o "{title}" {link} | tee {path_to_progress_file}')
        log.info('DOWNLOAD COMPLETE.')
        delete_progress_files()

        with open("downloaded-files.txt", "a") as f:
            f.write("\n" + title + " downloaded.") 
        
        for file in os.listdir():
            if file.split(".")[-1] in media_extensions:
                return f'/yt/{file}'

    elif request.form['button_clicked'] == 'MP3':

        log_this('chose Audio [MP3]')
        log.info(title)
        os.system(f'youtube-dl --newline -x --audio-format mp3 --audio-quality 0 '
        f'--embed-thumbnail -o "{title}" {link} | tee {path_to_progress_file}')
        log.info('DOWNLOAD COMPLETE.')
        delete_progress_files()

        with open("downloaded-files.txt", "a") as f:
            f.write("\n" + title + " downloaded.") 
        
        for file in os.listdir():
            if file.split(".")[-1] in media_extensions:
                return f'/yt/{file}'

# Send the converted/trimmed file to the following URL, where <filename> is the "value" for downloadFilePath
@yt.route("/yt/<filename>", methods=["GET"])
def download_yt_file(filename):
    just_extension = filename.split('.')[-1]
    if just_extension == "m4a":
        return send_from_directory(os.getcwd(), filename, mimetype="audio/mp4")
    else:
        return send_from_directory(os.getcwd(), filename)