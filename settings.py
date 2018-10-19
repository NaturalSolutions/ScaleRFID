#!/usr/bin/env python3

import logging
import logging.handlers


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
_consolelog = logging.StreamHandler()
_consolelog.setLevel(logging.DEBUG)
logger.addHandler(_consolelog)
_filelog = logging.handlers.RotatingFileHandler(
    'log/pesee.log', mode='a',
    maxBytes=500000, backupCount=10,
    encoding='utf-8')
_filelog.setLevel(logging.DEBUG)
logger.addHandler(_filelog)

ASSETS = '/home/pi/ScaleRFID/assets'
