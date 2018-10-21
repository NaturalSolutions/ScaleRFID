#!venv/bin/python3
# sudo ~/ScaleRFID/venv/bin/python3 -m ScaleRFID
# FIXME: https://github.com/topics/state-machine?l=python
import os
import signal
import time
from datetime import datetime
import queue
import multiprocessing as mp
import json

from . import (
    settings,
    hkb_input,
    KillSwitch
)
from .event_dispatcher import Event, EventDispatcher


logger = settings.logger
mp.log_to_stderr(10)
dispatcher = EventDispatcher()
hkb4 = hkb_input.HKB4Device(settings.HKB4_PORT)
killswitch = KillSwitch.KillSwitch(key_code=30, threshold=.500)

pool = []
q = mp.Queue(maxsize=4)


def shutdown(signum=0, frame=None):
    if signum > 0:
        signames = dict(
            (k, v) for v, k in list(signal.__dict__.items())
            if v.startswith('SIG'))
        logger.critical('Received signal %s', signames[signum])
    # q.close()
    # q.join_thread()
    if len(pool) > 0:
        for p in pool:
            # p.terminate()
            p.join()
    logger.critical('shutting down pid %s', os.getpid())
    exit(signum)


signal.signal(signal.SIGINT, shutdown)


def dispatch(event):
    _type = list(event.keys())[0]
    interfaced = Event(_type, event[_type])
    dispatcher.dispatch_event(interfaced)


def inputEvent(func):
    dispatcher.add_listener('inputEvent', func)


def shutdownEvent(func):
    dispatcher.add_listener('shutdownEvent', func)


def rfidEvent(func):
    dispatcher.add_listener('rfidEvent', func)


@shutdownEvent
def handle_shutdown(event: Event):
    logger.critical(
        'Received ShutdownEvent type: %s ts: %s code: %s',
        event.data['type'], event.data['ts'], event.data['code'])
    shutdown(event.data['code'])


@inputEvent
def handle_killswitch(event: Event):
    if (event.data.get('type', False)
            and event.data['type'] == 'keyrelease'
            and event.data['code'] == killswitch.key_code):

        killswitch.register(event.data['ts'])

        if killswitch.activated:
            logger.critical('Killswitch activated, sending shutdown event ...')
            dispatch({
                'shutdownEvent': {
                    'type': 'killswitch',
                    'ts': datetime.now().timestamp(),
                    'code': 0
                    }
                })
        elif killswitch.pending:
            logger.warn(
                ' delta: %s key_code: %s state: %s',
                '{:3.6f}µs'.format(killswitch._delta),
                event.data['code'], killswitch.state)


@inputEvent
def handle_any_key_release(event: Event):
    if (event.data.get('type', False)
            and event.data['type'] == 'keyrelease'):

        if (event.data['code'] == killswitch.key_code
                and (killswitch.activated or killswitch.pending)):
            if killswitch.activated:
                logger.debug('Activated killswitch')
            elif killswitch.pending:
                logger.debug('Pending killswitch activation')

        else:
            logger.info(' Processing scan_code %s', event.data['code'])


# main
try:
    KeyboardHandleService = mp.Process(
        name='KeyboardHandleService',
        target=hkb4.read,
        args=(True, q))
    KeyboardHandleService.start()
    if KeyboardHandleService:
        pool.append(KeyboardHandleService)
        print('Started KeyboardHandle service')
    else:
        logger.critical('Could not start KeyboardHandle service. Exiting.')
        shutdown(127)

    # main loop
    while not killswitch.activated:

        if q.qsize() > 0:
            event = q.get(timeout=1)
            dispatch(json.loads(event))

        time.sleep(.01)

except (queue.Full, Exception) as e:
    logger.critical(e)
    logger.debug(q)
    shutdown(127)
