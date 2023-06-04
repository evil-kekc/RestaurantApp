import logging
import os

BASE_DIR = os.path.abspath(os.path.curdir)


def setup_logger(log_file: str):
    logger = logging.getLogger('parser')
    logger.setLevel(logging.INFO)

    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_file = os.path.join(BASE_DIR, 'logs', f'{log_file}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
