import logging
# import Screen
from datetime import datetime
from time import sleep
from .event_dispatcher import Event, EventDispatcher
from .settings import KEYMAP


logger = logging.getLogger()
dispatcher = EventDispatcher()


def dispatch(event):
    _type = list(event.keys())[0]
    interfaced = Event(_type, event[_type])
    dispatcher.dispatch_event(interfaced)


def inputEvent(fn):
    dispatcher.add_listener('inputEvent', fn)


STARTING = 'STARTING ... WAIT'
DB_UPTODATE = 'DATABASE UP TO DATE'
DB_NOTFOUND = 'DATABASE FILE NOT FOUND'
DB_OUTDATED = 'DATABASE OUTDATED'
RFIDREADER_NOTFOUND = 'RFID READER NOT FOUND'
READY = 'SCAN READY'
EXPORT_ERROR = 'ERROR WHILE GENERATING EXCEL FILE'
UNREGISTERED_TAG = 'BIRD CHIP NOT FOUND'
UNREGISTERED_SPECIMEN = 'BIRD NOT IN DATABASE'
NO_POSITION = 'BIRD POSITION NOT IN DATABASE'
ALREADY_WEIGHED = 'BIRD ALREADY WEIGHED'
IMPOSSIBLE_WEIGHT = 'IMPOSSIBLE WEIGHT'
LOW_WEIGHT = '''\
LOW WEIGHT
1 - OK
2 - CANCEL'''
HIGH_WEIGHT = '''\
HIGH WEIGHT
1 - OK
2 - CANCEL'''
REMARKS = '''\
ANY REMARKS ?
1 - NO REMARK
2 - SKINNY
3 - FAT
4 - OTHER PROBLEM'''


class Prompt:
    def __init__(self, msg):
        # TODO: Screen interface
        logger.info(msg)
        self.answer = ''
        self.enquery = ''
        lines = msg.splitlines()
        if (len(lines) > 1
                and lines[2][0] in [v[0] for v in KEYMAP.values()]):
            self.enquery = msg

    def validate(self):
        lines = self.enquery.splitlines()
        if len(lines) > 1 and len(self.answer) > 0:
            match = [
                line[0] for line in lines
                if line.startswith(self.answer)]
            logger.debug('answer %s match %s', self.answer, match)
            return match

        return False

    def check(self):
        match = None
        while match is None:
            while (len(self.enquery) > 0  # FIXME DOING
                    and len(self.answer) == 0
                    and match is None):
                sleep(.01)
            match = self.validate()
        logger.info(match if match else 'no match')

    @classmethod
    @inputEvent
    def handle_input(cls, event: Event):

        if (event.data.get('type', False)
                and event.data['type'] == 'keyrelease'):
            logger.info(
                'Processing "%s" scan_code %s',
                KEYMAP[event.data['code']][0], event.data['code'])

            cls.answer = KEYMAP[event.data['code']][0]


if __name__ == '__main__':
    blah = Prompt(HIGH_WEIGHT)
    sleep(.5)
    dispatch({
        'inputEvent': {
            'type': 'keyrelease',
            'ts': datetime.now().timestamp(),
            'code': 46
        }
    })
    logger.debug(blah.answer)
    blah.check()
    dispatch({
        'inputEvent': {
            'type': 'keyrelease',
            'ts': datetime.now().timestamp(),
            'code': 30
        }
    })
    blah.check()
