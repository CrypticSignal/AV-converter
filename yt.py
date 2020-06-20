from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
import time
import urllib 
from bs4 import BeautifulSoup 
import shutil, os
from loggers import log_this, log

yt = Blueprint('yt',__name__)

def delete_progress_files():
    shutil.rmtree('static/progress')
    os.mkdir('static/progress')

@yt.route("/yt", methods=["POST"])
def yt_downloader():
    # youtube-dl can save the download progress to a text file,
    # set the name of the progress file to the time since the epoch.
    progress_filename = str(time.time())[:-8]
    # Create the file.
    with open(f'static/progress/{progress_filename}.txt', "w"): pass

    if request.form['button_clicked'] == 'yes':
        return progress_filename

    media_extensions = ["mp4", "webm", "opus", "mkv", "aac", "m4a", "mp3"]

    # Delete the videos that have already been downloaded so send_from_directory does not send back the wrong file.
    for file in os.listdir():
        if file.split(".")[-1] in media_extensions:
            os.remove(file)
        else:
            pass

    link = request.form['link']
    source = urllib.request.urlopen(f'{link}').read()
    soup = BeautifulSoup(source, features="html.parser")
    title = (soup.title.string[:-10]).replace('#', '')
    path_to_progress_file = f'static/progress/{progress_filename}.txt'

    if request.form['button_clicked'] == 'Video [best]':

        log_this('chose Video [best]')
        log.info(f'They want to download {title}')
        os.system(f'youtube-dl --newline {link} | tee {path_to_progress_file}')
        delete_progress_files()

        with open("downloaded-files.txt", "a") as f:
            f.write("\n" + title + " downloaded.") 

        for file in os.listdir():
            if file.split(".")[-1] in media_extensions:
                log.info(f'{file} downloaded.')
                return f'/yt/{file}'

    elif request.form['button_clicked'] == 'Video [MP4]':

        log_this('chose Video [MP4]')
        log.info(f'They want to download {title}')
        os.system(f'youtube-dl --newline -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" '
        f'{link} | tee {path_to_progress_file}')
        delete_progress_files()

        with open("downloaded-files.txt", "a") as f:
            f.write("\n" + title + " downloaded.") 
        
        for file in os.listdir():
            if file.split(".")[-1] in media_extensions:
                log.info(f'{file} downloaded.')
                return f'/yt/{file}'

    elif request.form['button_clicked'] == 'Audio [best]':

        log_this('chose Audio [best]')
        log.info(f'They want to download {title}')
        os.system(f'youtube-dl --newline -x {link} | tee {path_to_progress_file}')
        delete_progress_files()

        with open("downloaded-files.txt", "a") as f:
            f.write("\n" + title + " downloaded.") 
        
        for file in os.listdir():
            if file.split(".")[-1] in media_extensions:
                log.info(f'{file} downloaded.')
                return f'/yt/{file}'

    elif request.form['button_clicked'] == 'MP3':

        log_this('chose Audio [MP3]')
        log.info(f'They want to download {title}')
        os.system(f'youtube-dl --newline -x --audio-format mp3 --audio-quality 0 '
        f'--embed-thumbnail {link} | tee {path_to_progress_file}')
        delete_progress_files()

        with open("downloaded-files.txt", "a") as f:
            f.write("\n" + title + " downloaded.") 
        
        for file in os.listdir():
            if file.split(".")[-1] in media_extensions:
                log.info(f'{file} downloaded.')
                return f'/yt/{file}'

# Send the converted/trimmed file to the following URL, where <filename> is the "value" for downloadFilePath
@yt.route("/yt/<filename>", methods=["GET"])
def download_yt_file(filename):
    just_extension = filename.split('.')[-1]
    if just_extension == "m4a":
        return send_from_directory(os.getcwd(), filename, mimetype="audio/mp4", as_attachment=True)
    else:
        return send_from_directory(os.getcwd(), filename, as_attachment=True)