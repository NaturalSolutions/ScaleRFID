#!/usr/bin/python3

import random
# from transitions import Machine
from transitions.extensions import HierarchicalMachine as Machine
# import serial  # mocking for now
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
_consolelog = logging.StreamHandler()
_consolelog.setLevel(logging.DEBUG)
_consolelog.setFormatter(_formatter)
logger.addHandler(_consolelog)

RFID_READER_PORT = '/dev/ttyUSB0'


class RFIDTag():
    id_match_start = '$A0112OKD'
    id_match_end = '#'

    def __init__(self, reader):
        self.reader = reader
        self.code = None

    def read(self):
        code = self.reader.read(100)
        if code:
            code = code.split(RFIDTag.id_match_start)[1]
            self.code = code.split(RFIDTag.id_match_end)[0]
            logger.info('RFIDReader: read tag id: %s', self.code)

    def valid_tag(self):
        return True if self.code else False

    def invalid_tag(self):
        return False if not self.code else True

    def connected(self):
        return True if not self.reader._disconnected_error else False

    def not_connected(self):
        return True if self.reader._disconnected_error else False

    def on_enter_read(self, *args, **kwargs):
        self.read()

    def on_enter_validated(self, *args, **kwargs):
        logger.info(self.code)

    def on_enter_disconnected(self, *args, **kwargs):
        logger.critical('Dear operator, i\'m currently DISCONNECTED')


class RFIDReader():
    '''Active Reader Passive Tag (ARPT) system:
    an active reader, which transmits interrogator signals
    and also receives authentication replies from passive tags. '''

    def __init__(self, port=RFID_READER_PORT, speed=9600, timeout=None):
        self.port = port
        self.speed = speed
        self.timeout = timeout
        self._disconnected_error = False

    def read(self, nbytes=15):
        # try:
        #     with serial.Serial(
        #             self.port, self.speed, self, self.timeout) as reader:
        #         if nbytes and isinstance(nbytes, int):
        #             return reader.read(nbytes)
        #         else:
        #             return reader.read()
        # except serial.SerialException:
        #     raise DisconnectedError
        # except ValueError as e:
        #     raise MisconfiguredError

        # Mock
        from uuid import uuid4

        uid = uuid4()
        self._disconnected_error = bool(random.uniform(0, 1) > 0.66)  # noqa: S311,E501
        if self._disconnected_error:
            logger.critical('RFID_READER_DISCONNECTED_ERROR')
        return (RFIDTag.id_match_start + str(uid)[0:16] + RFIDTag.id_match_end
                if not self._disconnected_error
                else None)


reader = RFIDReader()
tag = RFIDTag(reader)

states = ['init', 'read', 'disconnected', 'validated']
transitions = [
    {'trigger': 'readtag', 'source': 'init', 'dest': 'read'},
    {'trigger': 'validate', 'source': 'read', 'dest': 'disconnected', 'conditions': 'not_connected'},  # noqa: E501
    {'trigger': 'validate', 'source': 'read', 'dest': 'validated', 'conditions': 'valid_tag'},         # noqa: E501
    {'trigger': 'validate', 'source': 'read', 'dest': 'init', 'conditions': 'invalid_tag'}             # noqa: E501
]
tag_fsm = Machine(
    model=tag, states=states, transitions=transitions, initial='init')
# tag.readtag()
# tag.validate()

collector_states = [
    'waiting',
    'collecting',
    {'name': 'tagreading', 'children': tag_fsm,
     'remap': {'validated': 'waiting'}}
]
collector_transitions = [
    ['collect', 'waiting', 'collecting'],
    ['wait', '*', 'waiting'],
    ['readatag', 'collecting', 'tagreading'],
    ['done', 'tagreading_read', 'waiting']
]
collector = Machine(
    states=collector_states,
    transitions=collector_transitions,
    initial='waiting')
collector.collect()
# collector.taginit()
collector.readatag()
collector.readtag()
# collector.validate()
collector.done()
collector.wait()
