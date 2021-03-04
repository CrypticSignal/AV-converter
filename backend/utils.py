from pathlib import Path
import os

from loggers import log


def clean_up():
    for file in os.listdir('downloads'):
        if Path(file).suffix in ['.part', '.webp', '.ytdl'] or '.temp.' in file:
            try:
                os.remove(file)
            except Exception:
                log.info(f'[CLEAN UP] Unable to delete {file}')
     

def delete_file(filepath):
    try:
        os.remove(filepath)
    except Exception as e:
        log.info(f'Unable to delete {filepath}:\n{e}')
    else:
        log.info(f'Deleted {filepath}')
