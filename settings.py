#!/usr/bin/env python3

import logging
import logging.handlers
import os

MODULE_ROOT = os.path.dirname(os.path.realpath(os.path.basename(__file__)))

LOG_DIR = os.path.join(MODULE_ROOT, 'log')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'pesee.log')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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

DB_PATH = os.path.expanduser(os.path.join(MODULE_ROOT, 'Public'))
os.makedirs(DB_PATH, exist_ok=True)

ASSETS = os.path.expanduser(os.path.join(MODULE_ROOT, 'assets'))
os.makedirs(ASSETS, exist_ok=True)

HKB4_PORT = '/dev/input/by-id/usb-413d_2107-event-mouse'
HKB4_KEYMAP = {
    30: {'1', 'a', 'q'},
    32: {'4', 'd'},
    46: {'3', 'c'},
    48: {'2', 'b'}
}

KILLSWITCH_KEYCODE = 30  # ought to be drawed from HKB4_KEYMAP keys
KILLSWITCH_THRESHOLD = .500  # ms

RFID_READER_PORT = '/dev/ttyUSB0'

STATES = [
    'waiting',
    'running',
    {
        'name': 'tagreading',
        'initial': 'init',
        'children': ['init', 'read', 'disconnected', 'validated']
    }, {
        'name': 'prompting',
        'initial': 'init',
        'children': ['init', 'read', 'resolved']
    }, {
        'name': 'querying',
        'initial': 'init',
        'children': ['init', 'read', 'known', 'unknown']
    }, {
        'name': 'weighing',
        'initial': 'init',
        'children': ['init', 'read', 'rejected', 'validated']
    }, {
        'name': 'updating',
        'initial': 'init',
        'children': ['init', 'read', 'failed', 'committed']
    }
]

TRANSITIONS = [
    {'trigger': 'run', 'source': 'waiting', 'dest': 'running', 'after': 'collect_tag'},  # noqa: E501
    ['wait', ['running', 'prompting_resolved'], 'waiting'],
    ['init', ['tagreading'], 'tagreading_init'],
    ['init', ['querying', ], 'querying_init'],
    ['init', ['weighing', 'prompt_resolved'], 'weighing_init'],
    ['init', ['updating'], 'updating_init'],
    ['init', ['prompting', ], 'prompting_init'],
    # check database update, create .CSV
    {'trigger': 'collect_tag', 'source': 'running', 'dest': 'tagreading', 'after': 'read_tag'},  # noqa: E501
    {'trigger': 'read_tag', 'source': 'tagreading_init', 'dest': 'tagreading_read', 'before': 'reader_read', 'after': 'validate_tag'},  # noqa: E501
    {'trigger': 'validate_tag', 'source': 'tagreading_read', 'dest': 'tagreading_disconnected', 'after': 'acknowledge'},  # noqa: E501
    {'trigger': 'validate_tag', 'source': 'tagreading_read', 'dest': 'tagreading_init', 'conditions': 'invalid_tag'},  # noqa: E501
    {'trigger': 'validate_tag', 'source': 'tagreading_read', 'dest': 'tagreading_validated', 'conditions': 'valid_tag', 'unless': 'reader_disconnected', 'after': 'collect_query'},  # noqa: E501
    {'trigger': 'collect_query', 'source': 'tagreading_validated', 'dest': 'querying', 'after': 'read_query'},  # noqa: E501
    {'trigger': 'read_query', 'source': 'querying_init', 'dest': 'querying_read', 'before': 'query_read', 'after': 'validate_query'},  # noqa: E501
    {'trigger': 'validate_query', 'source': 'querying_read', 'dest': 'querying_unknown', 'after': 'acknowledge'},  # unregistered specimen or unknown specimen position  # noqa: E501
    {'trigger': 'validate_query', 'source': 'querying_read', 'dest': 'querying_known', 'after': 'collect_weighing'},  # registered specimen and known specimen position  # noqa: E501
    # {'trigger': 'validate_query', 'source': 'querying_read', 'dest': 'querying_init'},  # some db query related error  # noqa: E501
    {'trigger': 'collect_weighing', 'source': 'querying_known', 'dest': 'weighing'},  # valid chip and known specimen and known position and not yet weighed today  # noqa: E501
    {'trigger': 'read_weight', 'source': 'weighing_init', 'dest': 'weighing_read', 'before': 'weight_read', 'after': 'validate_weight'},  # noqa: E501
    # {'trigger': 'validate_weight', 'source': 'weighing_read', 'dest': 'weighing_init'},  # disconnected scale_reader  # noqa: E501
    {'trigger': 'validate_weight', 'source': 'weighing_read', 'dest': 'weighing_rejected', 'after': 'acknowledge'},  # inconsistent or pathological weight  # noqa: E501
    {'trigger': 'validate_weight', 'source': 'weighing_read', 'dest': 'weighing_validated', 'after': 'collect_update'},  # normal specimen weight  # noqa: E501
    {'trigger': 'collect_update', 'source': 'weighing_validated', 'dest': 'updating', 'after': 'read_update'},  # noqa: E501
    {'trigger': 'read_update', 'source': 'updating_init', 'dest': 'updating_read', 'after': 'validate_update'},  # noqa: E501
    # {'trigger': 'validate_update', 'source': 'updating_read', 'dest': 'updating_init'},  # some db update related error  # noqa: E501
    {'trigger': 'validate_update', 'source': 'updating_read', 'dest': 'updating_failed', 'after': 'acknowledge'},  # db record update error  # noqa: E501
    {'trigger': 'validate_update', 'source': 'updating_read', 'dest': 'updating_committed', 'after': 'acknowledge'},  # COLLECT OPs COMMENTS  # noqa: E501
    ['read', 'prompting_init', 'prompting_read'],
    ['validate', 'prompting_read', 'prompting_resolved'],  # confirmed pathological weight or reconnected rdfidreader or acknowledged (outdated db or specimen unknown position or unregistered specimen or specimen invalid rf chip id)  # noqa: E501
    ['acknowledge', ['tagreading_disconnected', 'querying_unknown', 'weighing_rejected', 'updating_failed', 'updating_committed'], 'prompting'],  # noqa: E501
    # collect operator's comments
]
