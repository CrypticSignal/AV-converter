import os
from loggers import log


def delete_file(filepath):
    try:
        os.remove(filepath)
    except Exception as e:
        log.info(f'Unable to delete {filepath}:\n{e}')
    else:
        log.info(f'Deleted {filepath}')
