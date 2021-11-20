from datetime import datetime
import json
import os
from pathlib import Path
from time import time

from flask import Flask, request, send_from_directory, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from yt_dlp import YoutubeDL

from flask_app.utils import return_download_path
from logger import log

# The directory is relative to the location of run.py
download_dir = "downloads"


class Logger:
    def debug(self, msg):
        with open(session["yt_progress_url"], "a") as f:
            try:
                f.write(msg.strip() + "\n")
            except Exception as e:
                log.error(f"Unable to write the following ytdl progress:\n{msg.strip()}\n{e}")

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


def run_youtube_dl(video_link, options):
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(video_link, download=False)

        session["filename_stem"] = Path(ydl.prepare_filename(info)).stem
        try:
            ydl.download([video_link])
        except Exception as e:
            log.error(f'Error downloading {session["filename_stem"]}:\n{e}\n')
            log.info(f'Progress File: {session["yt_progress_url"]}')
            return str(e), 500
        else:
            os.remove(session["yt_progress_url"])
            return True


def run_yt_downloader(formdata, video_link):
    # Video (best quality)
    if formdata["button_clicked"] == "video_best":
        options = {
            "format": "bv*+ba/b",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "restrictfilenames": True,
            "logger": Logger(),
        }

        result = run_youtube_dl(video_link, options)

        if result == True:
            return return_download_path(download_dir)

        return result

    # MP4
    elif formdata["button_clicked"] == "mp4":
        options = {
            "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "restrictfilenames": True,
            "logger": Logger(),
        }

        result = run_youtube_dl(video_link, options)

        if result == True:
            return return_download_path(download_dir)

        return result

    # Audio (best quality)
    elif formdata["button_clicked"] == "audio_best":
        options = {
            "format": "ba/ba*/b",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "postprocessors": [{"key": "FFmpegExtractAudio"}],
            "restrictfilenames": True,
            "logger": Logger(),
        }

        result = run_youtube_dl(video_link, options)

        if result == True:
            return return_download_path(download_dir)

        return result

    # MP3
    elif formdata["button_clicked"] == "audio_mp3":
        options = {
            "format": "ba/ba*/b",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "writethumbnail": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "0",
                },
                {"key": "EmbedThumbnail"},
            ],
            "restrictfilenames": True,
            "logger": Logger(),
        }

        result = run_youtube_dl(video_link, options)

        if result == True:
            return return_download_path(download_dir)

        return result
