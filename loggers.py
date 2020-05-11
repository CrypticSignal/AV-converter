import logging
from datetime import datetime, timedelta
from flask import request 

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

logger = setup_logger('logger', 'info/Info.txt')
visit = setup_logger('visit', 'info/Visit.log')
user_agent_logger = setup_logger('user_agent_logger', 'info/UserAgent.txt')
socket_logger = setup_logger('socket_logger', 'info/Socket.txt')

# Socket.txt
def log_socket(message):
    current_datetime = (datetime.now() + timedelta(hours=1)).strftime('%d-%m-%y at %H:%M:%S')
    client = request.environ.get("HTTP_X_REAL_IP").split(',')[0]
    socket_logger.info(f'[{current_datetime}] {client} {message}.')

# Info.txt
def log_this(message):
    current_datetime = (datetime.now() + timedelta(hours=1)).strftime('%d-%m-%y at %H:%M:%S')
    client = request.environ.get("HTTP_X_REAL_IP").split(',')[0]
    logger.info(f'\n[{current_datetime}] {client} {message}')

# UserAgent.txt
def log_user_agent():
    current_datetime = (datetime.now() + timedelta(hours=1)).strftime('%d-%m-%y at %H:%M:%S')
    client = request.environ.get("HTTP_X_REAL_IP").split(',')[0]
    user_agent = request.headers.get('User-Agent')
    user_agent_logger.info(f'{current_datetime} | {client}\n{user_agent}')

# Visit.log
def log_visit(message):
    current_datetime = (datetime.now() + timedelta(hours=1)).strftime('%d-%m-%y at %H.%M.%S')
    client = request.environ.get("HTTP_X_REAL_IP").split(',')[0]
    visit.info(f'{client} {message} on {current_datetime}')