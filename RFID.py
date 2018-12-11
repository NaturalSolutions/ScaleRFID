#!venv/bin/python3

import serial  # mocking
from settings import logger, RFID_READER_PORT


class Error(Exception):
    pass


class DisconnectedError(Error):
    def __init__(self, message='RFID Reader Disconnected'):
        self.message = message


class TagReadError(Error):
    def __init__(self, message=None):
        self.message = message


class RFIDTag():
    id_match_start = '$A0112OKD'
    id_match_end = '#'

    def __init__(self, reader):
        self.reader = reader

    def read(self):
        code = self.reader.read(100)
        code = code.split(RFIDTag.id_match_start)[1]
        code = code.split(RFIDTag.id_match_end)[0]
        logger.debug('RFIDReader: read tag id: %s', code)
        validated = RFIDTag.validate(code)
        if validated:
            return code
        # otherwise a TagReadError should be raised during validation

    @staticmethod
    def validate(code):
        if len(code) == 16:
            return True
        else:
            raise TagReadError(
                'RFIDTag id length: expected 16 got {}'.format(len(code)))


class RFIDReader():
    '''Active Reader Passive Tag (ARPT) system:
    an active reader, which transmits interrogator signals
    and also receives authentication replies from passive tags. '''

    def __init__(self, port=RFID_READER_PORT, speed=9600, timeout=1):
        self.port = port
        self.speed = speed
        self.timeout = timeout

    def read(self, nbytes=15):
        try:
            with serial.Serial(
                    self.port, self.speed, self, self.timeout) as reader:
                if nbytes and isinstance(nbytes, int):
                    return reader.read(nbytes)
                else:
                    return reader.read()
        except serial.SerialException:
            raise DisconnectedError
        # mock
        # from uuid import uuid4
        #
        # uid = uuid4()
        # return RFIDTag.id_match_start + str(uid)[0:16] + RFIDTag.id_match_end


if __name__ == '__main__':
    from time import sleep
    from random import randint

    reader = RFIDReader
    while True:
        tag = RFIDTag(reader)
        tag.read()
        r = randint(0, 8)   # noqa: S311
        logger.debug('sleeping %s s', r)
        sleep(r)
