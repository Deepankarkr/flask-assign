import logging
from logging.handlers import RotatingFileHandler
import configparser
import datetime
import os
import sys


config = configparser.ConfigParser()
config.read('config.ini')


def setup_logger():
    log_files = config.get('constants', 'log_file_location') + str(
        datetime.datetime.now().strftime("%d_%b_%Y_%H_%M_%S")) + ".log"

    logger = logging.getLogger()
    logformat = config.get('constants', 'log_format', raw=True)
    datefmt = "%m-%d-%Y %H:%M"

    with open(log_files, 'a'):  
            pass  # Create an empty file

    logging.basicConfig(filename=log_files, level=logging.DEBUG, filemode="w", format=logformat, datefmt=datefmt)
    handler = logging.StreamHandler(sys.stdout)
    handler = RotatingFileHandler(log_files, mode='a', maxBytes=8 * 1024, encoding=None, delay=0)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
