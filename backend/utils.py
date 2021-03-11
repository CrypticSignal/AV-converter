from pathlib import Path
import os

from loggers import log

ytdl_format_codes = ['f137', 'f140', 'f251', 'f401']


def clean_up():
    for file in os.listdir('downloads'):
        if (Path(file).suffix in ['.part', '.webp', '.ytdl'] or file.split('.')[-2] in ytdl_format_codes or 
            '.part' in file):
            try:
                os.remove(os.path.join('downloads', file))
            except Exception as e:
                log.info(f'Unable to delete {file}:\n{e}')
     

def delete_file(filepath):
    try:
        os.remove(filepath)
    except Exception as e:
        log.info(f'Unable to delete {filepath}:\n{e}')


def empty_folder(folder_path):
    for file in os.listdir(folder_path):
        try:
            os.remove(os.path.join(folder_path, file))
        except Exception as e:
            log.info(f'Unable to delete {folder_path}/{file}:\n{e}')
        