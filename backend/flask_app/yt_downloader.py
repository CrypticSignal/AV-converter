from datetime import datetime
import json
import os
from pathlib import Path
from time import time

from flask import Flask, request, send_from_directory, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from yt_dlp import YoutubeDL

from flask_app.utils import return_download_path, write_to_file
from logger import log

# The directory is relative to the location of run.py
download_dir = "downloads"


def progress_hooks(data):
    if data["status"] == "downloading":
        downloaded_megabytes = round(data["downloaded_bytes"] / 1_000_000, 1)
        if data["total_bytes"] is not None:
            total_megabytes = round(data["total_bytes"] / 1_000_000, 1)
            progress_string = f"Downloaded {downloaded_megabytes}/{total_megabytes}MB"
        else:
            progress_string = f"{downloaded_megabytes}MB downloaded..."

        eta = data["eta"] if data["eta"] else "unknown"
        speed = f"{round(data['speed'] / 1000)}kb/s" if data["speed"] else "unknown"

        write_to_file(session["yt_progress_url"], f"{progress_string} @ {speed} [ETA: {eta}]")

    elif data["status"] == "finished":
        write_to_file(session["yt_progress_url"], "Postprocessing...")


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
            return "success"


def run_yt_downloader(formdata, video_link):
    # Video (best quality)
    if formdata["button_clicked"] == "video_best":
        options = {
            "format": "bv*+ba/b",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "restrictfilenames": True,
            "progress_hooks": [progress_hooks],
        }

        result = run_youtube_dl(video_link, options)

        if result == "success":
            return return_download_path(download_dir)

        return result

    # MP4
    elif formdata["button_clicked"] == "mp4":
        options = {
            "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "restrictfilenames": True,
            "progress_hooks": [progress_hooks],
        }

        result = run_youtube_dl(video_link, options)

        if result == "success":
            return return_download_path(download_dir)

        return result

    # Audio (best quality)
    elif formdata["button_clicked"] == "audio_best":
        options = {
            "format": "ba/ba*/b",
            "outtmpl": f"{download_dir}/%(title)s.%(ext)s",
            "postprocessors": [{"key": "FFmpegExtractAudio"}],
            "restrictfilenames": True,
            "progress_hooks": [progress_hooks],
        }

        result = run_youtube_dl(video_link, options)

        if result == "success":
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
            "progress_hooks": [progress_hooks],
        }

        result = run_youtube_dl(video_link, options)

        if result == "success":
            return return_download_path(download_dir)

        return result
