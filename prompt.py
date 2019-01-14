# import Screen
from datetime import datetime
from time import sleep
from .event_dispatcher import Event, EventDispatcher
from .settings import KEYMAP  # , DIALOGS  # , NOTIFICATIONS , logger
import logging

logger = logging.getLogger()
dispatcher = EventDispatcher()


def dispatch(event):
    _type = list(event.keys())[0]
    interfaced = Event(_type, event[_type])
    dispatcher.dispatch_event(interfaced)


def inputEvent(fn):
    dispatcher.add_listener('inputEvent', fn)


class Prompt:
    enquery = ''
    choices = dict()
    answer = ''

    def __init__(self, msg):
        # TODO: Screen interface
        logger.critical(msg)
        self.parse_msg(msg)

    def parse_msg(self, msg):
        lines = msg.splitlines()
        if (len(lines) > 1):
            Prompt.enquery = lines[0]
            Prompt.choices = {
                k: v
                for k, v in [l.split(' - ', 1) for l in lines[1:]]}

    def validate(self):
        logger.debug(
            'validation: %s %s "%s"',
            Prompt.enquery, Prompt.choices, Prompt.answer)
        choice = Prompt.choices.get(Prompt.answer, False)
        if choice:
            return choice, Prompt.answer

        return False

    def read(self):
        logger.debug(
            'reading: %s %s "%s"',
            Prompt.enquery, Prompt.choices, Prompt.answer)
        while (len(Prompt.choices.keys()) > 0 and len(Prompt.answer) == 0):
            sleep(.1)

    @inputEvent
    def handle_input(self, event: Event):
        if (event.data.get('type', False)
                and event.data['type'] == 'keyrelease'):
            logger.debug(
                'Processing keycode=%s scan_code=%s',
                KEYMAP[event.data['code']][0], event.data['code'])

            Prompt.answer = KEYMAP[event.data['code']][0]


if __name__ == '__main__':
    import threading
    from random import shuffle
    from .settings import DIALOGS  # , NOTIFICATIONS

    k = [30, 48, 46]
    shuffle(k)
    threads = []
    blah = Prompt(DIALOGS['HIGH_WEIGHT'])

    def fn1():
        sleep(.6)
        dispatch({
            'inputEvent': {
                'type': 'keyrelease',
                'ts': datetime.now().timestamp(),
                'code': k[0]
            }
        })

    def fn2():
        sleep(1.2)
        dispatch({
            'inputEvent': {
                'type': 'keyrelease',
                'ts': datetime.now().timestamp(),
                'code': k[1]
            }
        })

    def fn3():
        sleep(1.8)
        dispatch({
            'inputEvent': {
                'type': 'keyrelease',
                'ts': datetime.now().timestamp(),
                'code': k[2]
            }
        })

    for fn in {fn1, fn2, fn3}:
        t = threading.Thread(target=fn)
        threads.append(t)
        t.start()

    blah.read()
    valid = blah.validate()
    while not valid:
        blah.read()

    logger.debug('validated prompt: %s', valid)
    del blah
