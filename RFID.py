import serial
import logging


logger = logging.getLogger()


class RFIDReader():
    '''Active Reader Passive Tag (ARPT) system:
    an active reader, which transmits interrogator signals
    and also receives authentication replies from passive tags. '''

    def __init__(self, port, speed=9600, timeout=None):
        self.port = port
        self.speed = speed
        self.timeout = timeout
        self._disconnected_error = False
        self._misconfigured_error = False

    def read(self, nbytes=15):
        if self._disconnected_error:
            logger.error('RFID_READER_DISCONNECTED_ERROR')
        if self._misconfigured_error:
            logger.error('RFID_READER_MISCONFIGURED_ERROR')

        try:
            # with serial.Serial(
            #         self.port, self.speed, self, self.timeout) as reader:
            #     if nbytes and isinstance(nbytes, int):
            #          return reader.read(nbytes)
            #     else:
            #          return reader.read()
            # FIXME: MOCKING
            # return ('1234567890ABCDEF'.join(
            return ('0007200EEA'.join(
                [RFIDTag.id_match_start, RFIDTag.id_match_end])
                    if not self._disconnected_error
                    and not self._misconfigured_error else None)

        except serial.SerialException:
            # raise DisconnectedError
            self._disconnected_error = True
            logger.error('RFID_READER_DISCONNECTED_ERROR')

        except ValueError:
            # raise MisconfiguredError
            self._misconfigured_error = True
            logger.error('RFID_READER_MISCONFIGURED_ERROR')


class RFIDTag:
    id_match_start = '$A0112OKD'
    id_match_end = '#'

    def validate(self, code: str) -> str:
        if len(code) >= 1:
            code = code.split(RFIDTag.id_match_start, 1)[1]
            code = code.split(RFIDTag.id_match_end, 1)[0]

            logger.info('RFIDReader: validated tag id: %s', code)
            self.id = code.strip()
            return self.id

        return False
