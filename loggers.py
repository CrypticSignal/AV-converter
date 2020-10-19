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
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None: # This is the case when running locally.
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR'] 

# Create the ./logs directory if it does not already exist.
os.makedirs('logs', exist_ok=True)

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


downloads_today = 0
def log_downloads_per_day():
    # Create the file that will contain the downloads per day, if it doesn't already exist.
    if not os.path.exists('logs/downloads-per-day.txt'):
        open('logs/downloads-per-day.txt', 'x').close()

    file_contents = open('logs/downloads-per-day.txt', 'r').readlines()

    if file_contents and file_contents[0] == '\n':
        file_contents.pop(0)

    # The keys will be the date and the values will be the number of downloads.
    dates_to_downloads = {}

    for line in file_contents:
        date, downloads = line.split(' --> ')[0], line.split(' --> ')[1]
        dates_to_downloads[date] = downloads

    date_today = datetime.today().strftime('%d-%m-%Y')
    
    if date_today in dates_to_downloads:
        global downloads_today
        downloads_today += 1
        dates_to_downloads[date_today] = downloads_today
        # Use the dictionary to create a string in the format: date --> downloads
        contents_for_file = ''.join([f'{key} --> {value}' for key, value in dates_to_downloads.items()])
        # Write the string to downloads-per-day.txt
        with open('logs/downloads-per-day.txt', 'w') as f:
            f.write(contents_for_file)
    else:
        downloads_today = 1
        with open('logs/downloads-per-day.txt', 'a') as f:
            f.write(f'\n{date_today} --> {downloads_today}')