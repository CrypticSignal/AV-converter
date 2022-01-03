from datetime import datetime
from pathlib import Path
from time import time

from flask import Flask, request, send_from_directory, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from yt_dlp import YoutubeDL

from flask_app.utils import delete_file, return_download_path, write_to_file
from logger import log

# The directory is relative to the location of run.py
download_dir = "../"


def progress_hooks(data):
    if data["status"] == "downloading":
        tmp_filename = Path(data["tmpfilename"]).name
        tmp_filename_string = f"<br><i>Currently writing to <strong>{tmp_filename}<strong></i>"
    
        downloaded_mb = round(data["downloaded_bytes"] / 1_000_000, 1)
        log.info(f"Downloaded: {downloaded_mb}")

        if "total_bytes" in data and data["total_bytes"]:
            total_mb = round(data["total_bytes"] / 1_000_000, 1)
        elif "total_bytes_estimate" in data and data["total_bytes_estimate"]:
            total_mb = round(data["total_bytes_estimate"] / 1_000_000, 1)
        else:
            total_mb = None

        if total_mb:
            log.info(f"Total: {total_mb}")
            percentage_progress = round((downloaded_mb / total_mb) * 100, 1)
            progress_string = f"{percentage_progress}% of ~{total_mb} MB downloaded"
        else:
            progress_string = f"{downloaded_mb} MB downloaded"

        speed = f"{round(data['speed'] / 1000)} kb/s" if data["speed"] else "unknown"
        eta = data["eta"] if data["eta"] else "unknown"

        if eta != "unknown":
            minutes, seconds = divmod(eta, 60)
            eta = f"{minutes:02}:{seconds:02}"

        write_to_file(
            session["yt_progress_url"],
            f"{progress_string} @ {speed} [ETA: {eta}]{tmp_filename_string}",
        )

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
            delete_file(session["yt_progress_url"])
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
