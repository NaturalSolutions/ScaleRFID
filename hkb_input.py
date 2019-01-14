#!venv/bin/python3

import os
import struct
from datetime import datetime, timedelta
import json
import logging

assert os.geteuid() == 0, '''You must be root to read from the keyboard device interface.'''  # noqa: E501,S101
assert datetime.resolution <= timedelta(microseconds=1)  # noqa: S101
µs = 1000000

logger = logging.getLogger()


class HKB4Device():
    # https://pcsensor.com/pcsensor-usb-handle-lkeyboard-6-buttons-laptop-handle-keyboard-hk4.html  # noqa: E501
    def __init__(self, path, fmt='llHHi'):
        self.path = path
        self.format = fmt
        self.continuously = False
        self._disconnected_error = False

    def read(self, continuously=False, queue=None):  # Event | void
        self.continuously = self.continuously or continuously if continuously else False  # noqa: E501
        try:
            with open(self.path, 'rb') as self.device:
                event = None

                if not self.continuously:
                    event = self.get_event()
                    return event
                else:
                    while self.continuously and queue:
                        event = self.get_event()
                        queue.put_nowait(event)
                    queue.close()
        except (FileNotFoundError, Exception):
            logger.error('HBK4_INPUT_DISCONNECTED_ERROR')
            self._disconnected_error = True
            raise

    def get_event(self):
        event = None
        while not event:
            data = self.device.read(struct.calcsize(self.format))
            event = self._extract_event(data)
        return event

    def _extract_event(self, data):
        sec, usec, type_, code, press = struct.unpack(self.format, data)
        if type_ == 1:
            return json.dumps({
                'inputEvent': {
                    'type': 'keypress' if press > 0 else 'keyrelease',
                    'ts': sec + (usec / µs),
                    'code': code
                }
            })


if __name__ == '__main__':
    # noqa: C901
    logger.setLevel(logging.DEBUG)
    _consolelog = logging.StreamHandler()
    _consolelog.setLevel(logging.DEBUG)
    logger.addHandler(_consolelog)

    hkb4 = HKB4Device('/dev/input/by-id/usb-413d_2107-event-mouse')
    # event = hkb4.read()
    # print(event)

    import time
    import signal
    import multiprocessing as mp
    # import json
    from event_dispatcher import Event, EventDispatcher

    pool = []
    q = mp.Queue(maxsize=4)
    dispatcher = EventDispatcher()

    def shutdown(signum=0, frame=None):
        if signum > 0:
            signames = dict((k, v) for v, k in list(signal.__dict__.items())
                            if v.startswith('SIG'))
            logger.critical('Received signal %s', signames[signum])
        logger.critical('shuting down %s', os.getpid())
        for p in pool:
            p.terminate()
        exit

    signal.signal(signal.SIGINT, shutdown)

    def dispatch(event):
        _type = list(event.keys())[0]
        interfaced = Event(_type, event[_type])
        dispatcher.dispatch_event(interfaced)

    def inputEvent(fn):
        dispatcher.add_listener('inputEvent', fn)

    class KillSwitch:
        _STATES = [False, 'PENDING1', 'PENDING2', 'ACTIVATED']

        def __init__(self, key_code=30, threshold=.500):
            self.state = self._STATES[0]
            self.key_code = key_code
            self.threshold = threshold
            self._last = datetime.now()

        def activate(cb: callable, *args, **kwargs):
            cb(*args, **kwargs)

        @property
        def activated(self):
            return self._STATES.index(self.state) == len(self._STATES) - 1

        @property
        def pending(self):
            return self._STATES[0] < self._STATES.index(self.state) < len(self._STATES)  # noqa: E501

        def increment(self):
            self.state = self._STATES[self._STATES.index(self.state) + 1]

    killswitch = KillSwitch()

    @inputEvent
    def killswitch_event(event: Event):
        if (event.data.get('type', False)
                and event.data['type'] == 'keyrelease'
                and event.data['code'] == killswitch.key_code):

            if (event.data['ts'] - killswitch._last.timestamp() < killswitch.threshold):  # noqa: E501
                killswitch.increment()
                logger.debug(
                    ' delta: %s key_code: %s state: %s',
                    event.data['ts'] - killswitch._last.timestamp(),
                    event.data['code'],
                    killswitch.state)
                if killswitch.activated:
                    logger.debug('Killswitch activated')
                    shutdown(signum=0)
            else:
                killswitch.state = killswitch._STATES[0]
            killswitch._last = datetime.now()

    @inputEvent
    def any_key_release(event: Event):
        if (event.data.get('type', False)
                and event.data['type'] == 'keyrelease'):
            if event.data['code'] == killswitch.key_code:
                if killswitch.activated:
                    logger.debug('Activated killswitch')
                elif killswitch.pending:
                    logger.debug('Pending killswitch activation')
                else:
                    logger.info(' Processing scan_code %s', event.data['code'])

    # main
    p = mp.Process(
        name='hkb4_log_producer_service',
        target=hkb4.read, args=(True, q))
    pool.append(p)

    try:
        p.start()
        print('Started {}'.format(p.name))

        # def consume():
        while not killswitch.activated:
                # print('get q cont %s', hkb4.continuously)
            if q.qsize() > 0:
                event = q.get(timeout=1)
                dispatch(json.loads(event))
                hkb4.continuously = False  # FIXME
            time.sleep(.01)

        # c = mp.Process(
        #     name='hkb4_log_consumer_service',
        #     target=consume, )
        # c.start()
        # print('Started {}'.format(c.name))
        # pool.append(c)
    except Exception as e:
        print(e)
