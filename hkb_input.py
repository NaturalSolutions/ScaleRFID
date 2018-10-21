#!venv/bin/python3

import os
import struct
from datetime import datetime, timedelta
import json
import logging

assert os.geteuid() == 0, '''You must be root to read from the keyboard device interface.'''  # noqa: E501
assert datetime.resolution <= timedelta(microseconds=1)
µs = 1000000

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
_consolelog = logging.StreamHandler()
_consolelog.setLevel(logging.DEBUG)
logger.addHandler(_consolelog)


class inputHKbDevice():
    # https://pcsensor.com/pcsensor-usb-handle-lkeyboard-6-buttons-laptop-handle-keyboard-hk4.html  # noqa: E501
    def __init__(self, path, fmt='llHHi'):
        self.path = path
        self.format = fmt
        self.continuously = False

    def read(self, continuously=False, queue=None):  # Event | void
        self.continuously = self.continuously or continuously if continuously else False  # noqa: E501
        with open(self.path, 'rb') as self.device:
            event = None

            if not self.continuously:
                event = self.get_event()
                return event
            else:
                while self.continuously and queue:
                    event = self.get_event()
                    queue.put_nowait(event)

    def get_event(self):
        event = None
        while not event:
            data = self.device.read(struct.calcsize(self.format))
            event = self._extract_event(data)
        return event

    def _extract_event(self, data):
        sec, usec, type, code, press = struct.unpack(self.format, data)
        if type == 1:
            return json.dumps({
                'inputEvent': {
                    'type': 'keypress' if press > 0 else 'keyrelease',
                    'ts': sec + (usec / µs),
                    'code': code
                }
            })


if __name__ == '__main__':

    hkb4 = inputHKbDevice('/dev/input/by-id/usb-413d_2107-event-mouse')
    # event = hkb4.read()
    # print(event)

    import time
    import signal
    import multiprocessing as mp
    # import json
    from hkb_events import dispatch, inputEvent

    pool = []
    q = mp.Queue(maxsize=4)

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

    class killswitch:
        _STATES = [False, 'PENDING1', 'PENDING2', 'ACTIVATED']

        def __init__(self, key_code=30, threshold=.500):
            self.state = self._STATES[0]
            self.key_code = key_code
            self.threshold = threshold
            self._last = datetime.now()

        @property
        def activated(self):
            return self._STATES.index(self.state) == len(self._STATES) - 1

        @property
        def pending(self):
            return self._STATES[0] < self._STATES.index(self.state) < len(self._STATES)  # noqa: E501

        def increment(self):
            self.state = self._STATES[self._STATES.index(self.state) + 1]

    switch = killswitch()

    @inputEvent
    def process_input_event(event):
        if (event.data['type'] == 'keyrelease'
                and event.data['code'] == switch.key_code):
            if event.data['ts'] - switch._last.timestamp() < switch.threshold:
                switch.increment()
                logger.debug(
                    ' delta: %s key_code: %s state: %s',
                    event.data['ts'] - switch._last.timestamp(),
                    event.data['code'],
                    switch.state)
                if switch.activated:
                    logger.debug('Killswitch activated')
                    shutdown(signum=0)
            else:
                switch.state = switch._STATES[0]
            switch._last = datetime.now()

    @inputEvent
    def any_key_release(event):
        if (event.data['type'] == 'keyrelease'):
            if event.data['code'] == switch.key_code:
                if switch.activated:
                    logger.debug('Activated killswitch')
                elif switch.pending:
                    logger.debug('Pending killswitch activation')
                else:
                    logger.info(' Processing scan_code %s', event.data['code'])

    p = mp.Process(
        name='hkb4_log_producer_service',
        target=hkb4.read, args=(True, q))
    pool.append(p)

    try:
        p.start()
        print('Started {}'.format(p.name))

        # def consume():
        while not switch.activated:
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
