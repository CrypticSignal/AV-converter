from datetime import datetime
import logging
import os
from pathlib import Path
import shutil

from ffmpeg import probe
from flask import request, session
from user_agents import parse

from flask_app import db  # Import db from __init__.py
from flask_app.models import ConverterDB, DownloaderDB
from logger import log


def clean_downloads_folder(download_dir, filename_stem):
    # Empty the downloads folder if there is less than 500 MB free storage space.
    free_space = shutil.disk_usage("/")[2]
    free_space_gb = free_space / 1_000_000
    if free_space_gb < 500:
        empty_folder(download_dir)
    else:
        ytdl_format_codes = ["f137", "f140", "f251", "f401"]
        for file in os.listdir(download_dir):
            if filename_stem in file and Path(file).suffix != "":
                if (
                    Path(file).suffix in [".webp", ".ytdl"]
                    or file.split(".")[-2] in ytdl_format_codes
                ):
                    try:
                        os.remove(os.path.join(download_dir, file))
                    except Exception:
                        log.error(f"Unable to delete {file}")


def delete_file(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)


def detailed_log(message):
    current_datetime = datetime.now().strftime("%d-%m-%y at %H:%M:%S")
    ua_string = request.headers.get("User-Agent")
    user_agent = parse(ua_string)
    log.info("------------------------------------------------------------------------------------")
    log.info(f"[{current_datetime}] {get_ip()} {message}\n {user_agent}")


def empty_folder(folder_path):
    for file in os.listdir(folder_path):
        try:
            os.remove(os.path.join(folder_path, file))
        except Exception as e:
            log.error(f"Unable to delete {folder_path}/{file}:\n{e}")
        else:
            log.info(f"{file} deleted.")


def get_file_duration(self):
    return float(probe(self._video_path)["format"]["duration"])


# https://stackoverflow.com/a/49760261/13231825
def get_ip():
    if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
        return request.environ["REMOTE_ADDR"]
    else:
        return request.environ["HTTP_X_FORWARDED_FOR"]


# This function returns True if the first audio stream is mono.
def is_mono_audio(filepath):
    try:
        first_audio_stream = [
            stream for stream in probe(filepath)["streams"] if stream["codec_type"] == "audio"
        ][0]
    except Exception as e:
        log.error(f"ffprobe was unable to detect an audio stream in {filepath}:\n{e}")
    else:
        if first_audio_stream["channels"] == 1:
            return True

    return False


def return_download_path(download_dir):
    unwanted_filetypes = [".part", ".jpg", ".ytdl", ".webp"]
    # Get the filename of the completed download.
    filename = [
        file
        for file in os.listdir(download_dir)
        if Path(file).suffix not in unwanted_filetypes
        and Path(file).stem == session["filename_stem"]
    ][0]

    clean_downloads_folder(download_dir, Path(filename).stem)

    filesize = round((os.path.getsize(os.path.join(download_dir, filename)) / 1_000_000), 2)
    update_downloader_database(filesize)

    # Remove any hashtags or pecentage symbols as they cause an issue
    # and make the filename more aesthetically pleasing by replacing the underscores with spaces.
    new_filename = filename.replace("#", "").replace("%", "").replace("_", " ")

    try:
        # Rename the file.
        os.replace(
            os.path.join(download_dir, filename),
            os.path.join(download_dir, new_filename),
        )
    except Exception as e:
        log.error(f"Unable to rename {filename} to {new_filename}:\n{e}")
        return os.path.join(download_dir, filename)
    else:
        log.info(f"{new_filename} | {filesize} MB")
        # Update the list of videos downloaded.
        with open("../downloads.txt", "a+") as f:
            f.seek(0)
            if new_filename not in f.read():
                f.write(f"\n{new_filename}")
        # Return the download link.
        return os.path.join("api", "download", new_filename)

def update_converter_database():
    # Use the get_ip function imported from loggers.py
    user_ip = get_ip()
    # Query the database by IP.
    user = ConverterDB.query.filter_by(ip=user_ip).first()
    if user:
        string = "time" if user.times_used == 1 else "times"
        log.info(f"This user has used the converter {user.times_used} {string} before.")
        user.times_used += 1
        db.session.commit()
    else:
        new_user = ConverterDB(ip=user_ip, times_used=1)
        db.session.add(new_user)
        db.session.commit()


def update_downloader_database(mb_downloaded):
    # Use the get_ip function imported from loggers.py
    user_ip = get_ip()
    # Query the database by IP.
    user = DownloaderDB.query.filter_by(ip=user_ip).first()
    if user:
        user.times_used += 1
        user.mb_downloaded += mb_downloaded
        db.session.commit()
    else:
        new_user = DownloaderDB(ip=user_ip, times_used=1, mb_downloaded=mb_downloaded)
        db.session.add(new_user)
        db.session.commit()


def write_to_file(filepath, content, mode="w"):
    with open(filepath, mode) as f:
        f.write(content)
