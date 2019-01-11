# import Screen
from datetime import datetime
from time import sleep
from .event_dispatcher import Event, EventDispatcher
from .settings import KEYMAP, logger


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
    answer = ''

    def __init__(self, msg):
        # TODO: Screen interface
        logger.info(msg)
        Prompt.answer = ''
        self.enquery = ''
        lines = msg.splitlines()
        if (len(lines) > 1
                and lines[2][0] in [v[0] for v in KEYMAP.values()]):
            self.enquery = msg

    def validate(self):
        lines = self.enquery.splitlines()
        label = lines[0]
        choice = [line[0] for line in lines[1:] if line[0] == Prompt.answer]
        if len(choice) == 1:
            return label, choice[0]

        return False

    def read(self):
        while (len(self.enquery) > 0
                and len(Prompt.answer) == 0):
            sleep(.1)

    @classmethod
    @inputEvent
    def handle_input(cls, event: Event):
        if (event.data.get('type', False)
                and event.data['type'] == 'keyrelease'):
            logger.info(
                'Processing keycode=%s scan_code=%s',
                KEYMAP[event.data['code']][0], event.data['code'])

            Prompt.answer = KEYMAP[event.data['code']][0]


if __name__ == '__main__':
    import threading

    threads = []
    blah = Prompt(HIGH_WEIGHT)

    def fn1():
        sleep(.6)
        dispatch({
            'inputEvent': {
                'type': 'keyrelease',
                'ts': datetime.now().timestamp(),
                'code': 48  # 30
            }
        })

    def fn2():
        sleep(1.2)
        dispatch({
            'inputEvent': {
                'type': 'keyrelease',
                'ts': datetime.now().timestamp(),
                'code': 46
            }
        })

    def fn3():
        sleep(2)
        dispatch({
            'inputEvent': {
                'type': 'keyrelease',
                'ts': datetime.now().timestamp(),
                'code': 30  # 48
            }
        })

    for fn in {fn1, fn2, fn3}:
        t = threading.Thread(target=fn)
        threads.append(t)
        t.start()
    blah.read()
    valid = blah.validate()
    if valid:
        logger.debug('validated prompt: %s', valid)
        del blah
