import os
from pathlib import Path
import shutil

from loggers import log

ytdl_format_codes = ["f137", "f140", "f251", "f401"]


def clean_up(filename_stem):
    empty_folder("yt-progress")
    # Empty the downloads folder if there is less than 2 GB free storage space.
    free_space = shutil.disk_usage("/")[2]
    free_space_gb = free_space / 1_000_000_000
    if free_space_gb < 2:
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
