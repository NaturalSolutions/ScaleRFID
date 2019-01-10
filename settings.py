#!/usr/bin/env python3

import logging
import logging.handlers
import os

root = os.path.dirname(os.path.realpath(os.path.basename(__file__)))

LOG_DIR = os.path.join(root, 'log')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'pesee.log')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
_formatter = logging.Formatter(
    '%(asctime)s %(levelname)s - %(message)s')
_consolelog = logging.StreamHandler()
_consolelog.setLevel(logging.DEBUG)
_consolelog.setFormatter(_formatter)
logger.addHandler(_consolelog)
_filelog = logging.handlers.RotatingFileHandler(
    LOG_FILE, mode='a',
    maxBytes=500000,
    backupCount=10,
    encoding='utf-8')
_filelog.setLevel(logging.DEBUG)
_filelog.setFormatter(_formatter)
logger.addHandler(_filelog)

DB_PATH = os.path.expanduser(os.path.join(root, 'Public'))
os.makedirs(DB_PATH, exist_ok=True)

ASSETS = os.path.expanduser(os.path.join(root, 'assets'))
os.makedirs(ASSETS, exist_ok=True)

HKB4_PORT = '/dev/input/by-id/usb-413d_2107-event-mouse'
RFID_READER_PORT = '/dev/ttyUSB0'
