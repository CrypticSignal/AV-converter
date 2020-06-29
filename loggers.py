import os, logging
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
 
def get_ip(): # The contents of this function is from https://stackoverflow.com/a/49760261/13231825
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy

# Create the ./logs directory if it does not already exist.
<<<<<<< HEAD
os.makedirs('logs', exist_ok=True)
    
=======
os.makedirs('logs', exist_ok=True)   

>>>>>>> 778ffc882f331d5fc307b5282c5d98eabbf73249
log = setup_logger('log', 'logs/info.txt')
visit = setup_logger('visit', 'logs/visit.log')

# info.txt
def log_this(message):
    current_datetime = datetime.now().strftime('%d-%m-%y at %H:%M:%S')
    client = get_ip()
    log.info(f'\n[{current_datetime}] {client} {message}')

# visit.log
def log_visit(message):
    current_datetime = datetime.now().strftime('%d-%m-%y at %H.%M.%S')
    client = get_ip()
    visit.info(f'{client} {message} on {current_datetime}')
