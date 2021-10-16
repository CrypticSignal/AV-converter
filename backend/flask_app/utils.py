from datetime import datetime
import logging
import os
from pathlib import Path
import shutil

from ffmpeg import probe
from flask import request
from user_agents import parse

from flask_app import db # Import db from __init__.py
from flask_app.models import ConverterDB


ytdl_format_codes = ["f137", "f140", "f251", "f401"]


def clean_up(filename_stem):
    # Empty the downloads folder if there is less than 500 MB free storage space.
    free_space = shutil.disk_usage("/")[2]
    free_space_gb = free_space / 1_000_000
    if free_space_gb < 500:
        empty_folder("downloads")
    else:
        for file in os.listdir("downloads"):
            if filename_stem in file and Path(file).suffix != "":
                if (
                    Path(file).suffix in [".part", ".webp", ".ytdl"]
                    or file.split(".")[-2] in ytdl_format_codes
                    or ".part" in file
                ):
                    try:
                        os.remove(os.path.join("downloads", file))
                    except Exception as e:
                        log.info(f"[CLEAN UP] Unable to delete {file}:\n{e}")


def delete_file(filepath):
    try:
        os.remove(filepath)
    except Exception as e:
        log.info(f"Unable to delete {filepath}:\n{e}")
    else:
        log.info(f"{filepath} deleted.")


def empty_folder(folder_path):
    for file in os.listdir(folder_path):
        try:
            os.remove(os.path.join(folder_path, file))
        except Exception as e:
            log.info(f"Unable to delete {folder_path}/{file}:\n{e}")
        else:
            log.info(f"{file} deleted.")

        
def get_ip():  # The contents of this function is from https://stackoverflow.com/a/49760261/13231825
    if (
        request.environ.get("HTTP_X_FORWARDED_FOR") is None
    ):  # This is the case when running locally.
        return request.environ["REMOTE_ADDR"]
    else:
        return request.environ["HTTP_X_FORWARDED_FOR"]


# This function returns True if the first audio stream is mono.
def is_mono_audio(filepath):
    try:
        first_audio_stream = [
            stream for stream in probe(filepath)["streams"] if stream["codec_type"] == "audio"
        ][0]
    except Exception:
        log.info(f"ffprobe was unable to detect an audio stream in {filepath}")
    else:
        if first_audio_stream["channels"] == 1:
            return True

    return False


def log_this(message):
    current_datetime = datetime.now().strftime("%d-%m-%y at %H:%M:%S")
    client = get_ip()
    ua_string = request.headers.get("User-Agent")
    user_agent = parse(ua_string)
    log.info(f"\n[{current_datetime}] {client} {message}\n{str(user_agent)}")


def setup_logger(name, log_file):
    log_format = logging.Formatter("%(message)s")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(log_format)
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(10)
    logger.addHandler(file_handler)
    return logger


def update_database():
    # Use the get_ip function imported from loggers.py
    user_ip = get_ip()
    # Query the database by IP.
    user = ConverterDB.query.filter_by(ip=user_ip).first()
    if user:
        user.times_used+= 1
        db.session.commit()
    else:
        new_user = ConverterDB(ip=user_ip, times_used=1)
        db.session.add(new_user)
        db.session.commit()

log = setup_logger("log", "./logs/info.txt")
