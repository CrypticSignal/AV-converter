import logging
from flask import request
from datetime import datetime

def setup_logger(name, log_file):
    log_format = logging.Formatter('%(message)s')
    file_handler = logging.FileHandler(log_file)        
    file_handler.setFormatter(log_format)
    logger = logging.getLogger(name)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.setLevel(10)
    logger.addHandler(file_handler)
    return logger

log = setup_logger('log', 'logs/info.txt')
visit = setup_logger('visit', 'logs/visit.log')

# Info.txt
def log_this(message):
    current_datetime = datetime.now().strftime('%d-%m-%y at %H:%M:%S')
    client = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
    log.info(f'\n[{current_datetime}] {client} {message}')

# Visit.log
def log_visit(message):
    current_datetime = datetime.now().strftime('%d-%m-%y at %H.%M.%S')
    client = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
    visit.info(f'{client} {message} on {current_datetime}')
