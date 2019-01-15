# import Screen
from datetime import datetime
from time import sleep
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Prompt:
    enquery = ''
    choices = dict()
    answer = ''
    ts = ''
    type_ = ''
    value_ = ''

    def from_str(cls, type_, value_):
        # TODO: Screen interface
        cls.type_ = type_
        cls.value_ = value_
        if type_ is not None and value_ is not None:
            logger.debug(type_[value_])
            return cls.parse_msg(type_[value_])
        else:
            return cls

    def __repr__(self):
        return '<Prompt enquery={} choices={} answer={} ts={}>'.format(
            Prompt.enquery, Prompt.choices, Prompt.answer, Prompt.ts)

    __str__ = __repr__

    @classmethod
    def parse_msg(cls, msg):
        lines = msg.splitlines()
        if (len(lines) > 1):
            cls.enquery = lines[0]
            cls.choices = {
                k: v
                for k, v in [l.split(' - ', 1) for l in lines[1:]]}
        else:
            cls.enquery = msg
            cls.choices = dict()

        cls.ts = datetime.now()
        return cls

    @classmethod
    def validate(cls):
        if (isinstance(cls.choices, dict) and isinstance(cls.answer, str)
                and cls.enquery):
            # dialog
            if cls.choices and cls.answer:
                logger.debug(
                    'Validation dialog: enquery=%s choices=%s',
                    cls.enquery, cls.choices)
                choice = cls.choices.get(cls.answer, None)
                return choice, cls.answer if choice else False
            # notification
        elif cls.choices == {}:
                logger.debug(
                    'Validation notification: enquery=%s', cls.enquery)
                return True

        return False

    @classmethod
    def read(cls):
        logger.critical('PROMPT_READ: %s', cls.__str__(cls))
        while (len(cls.choices.keys()) > 0 and cls.answer == ''):
            sleep(.1)


if __name__ == '__main__':
    # sudo -H /my_venv/bin/python3 -m ScaleRFID.prompt
    import threading
    from random import shuffle
    from .settings import KEYMAP, DIALOGS, NOTIFICATIONS
    from .event_dispatcher import Event, EventDispatcher

    dispatcher = EventDispatcher()
    k = [30, 48, 46]
    shuffle(k)
    threads = []
    blah = Prompt.from_str(Prompt, DIALOGS, 'HIGH_WEIGHT')

    def dispatch(event):
        _type = list(event.keys())[0]
        interfaced = Event(_type, event[_type])
        dispatcher.dispatch_event(interfaced)

    def inputEvent(fn):
        dispatcher.add_listener('inputEvent', fn)

    @inputEvent
    def handle_input(event: Event):
        if (event.data.get('type', False)
                and event.data['type'] == 'keyrelease'):
            logger.debug(
                'Processing keycode=%s scan_code=%s',
                KEYMAP[event.data['code']][0], event.data['code'])

        Prompt.answer = KEYMAP[event.data['code']][0]

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
    for t in threads:
        t.join()

    logger.debug('validating notification')
    blah = Prompt.from_str(Prompt, NOTIFICATIONS, 'UNREGISTERED_SPECIMEN')
    blah.read()
    valid = blah.validate()
