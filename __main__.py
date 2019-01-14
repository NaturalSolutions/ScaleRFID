#!venv/bin/python3
# sudo apt install -yq graphviz graphviz-dev
# sudo ~/ScaleRFID/venv/bin/python3 -m ScaleRFID
import os
import signal
import time
from datetime import datetime
import queue
import multiprocessing as mp
import json

from transitions.extensions import MachineFactory

from . import (
    settings,
    hkb_input,
    KillSwitch,
    DB
)
from .event_dispatcher import Event, EventDispatcher
from .RFID import RFIDReader
from .system import System

logger = settings.logger
mp.log_to_stderr(10)
dispatcher = EventDispatcher()
assert os.path.exists(settings.HKB4_PORT)  # noqa: S101
hkb4 = hkb_input.HKB4Device(settings.HKB4_PORT)
killswitch = KillSwitch.KillSwitch(
    key_code=settings.KILLSWITCH_KEYCODE,
    threshold=settings.KILLSWITCH_THRESHOLD)
reader = RFIDReader(settings.RFID_READER_PORT)


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
            p.terminate()
            time.sleep(0.1)
            if not p.is_alive():
                p.join(timeout=1.0)
    q.close()
    logger.critical('shutting down pid %s', os.getpid())
    exit(signum)


signal.signal(signal.SIGINT, shutdown)


def dispatch(event):
    _type = list(event.keys())[0]
    interfaced = Event(_type, event[_type])
    dispatcher.dispatch_event(interfaced)


def inputEvent(fn):
    dispatcher.add_listener('inputEvent', fn)


def shutdownEvent(fn):
    dispatcher.add_listener('shutdownEvent', fn)


def rfidEvent(fn):
    dispatcher.add_listener('rfidEvent', fn)


@shutdownEvent
def handle_shutdown(event: Event):
    logger.critical(
        'Received ShutdownEvent type: %s ts: %s code: %s',
        event.data['type'], event.data['ts'], event.data['code'])
    shutdown(event.data['code'])


@inputEvent
def handle_killswitch(event: Event):
    if (event.data.get('type', False)
            and event.data['type'] == 'keypress'
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
            logger.debug(' Processing scan_code %s', event.data['code'])


# main
try:
    KeyboardHandleService = mp.Process(
        name='KeyboardHandleService',
        target=hkb4.read,
        args=(True, q))
    KeyboardHandleService.start()
    if KeyboardHandleService.is_alive():
        pool.append(KeyboardHandleService)
        logger.info('Started KeyboardHandle service')
    else:
        logger.critical('Could not start KeyboardHandle service. Exiting.')
        shutdown(signal.SIGINT)

    # class KeyboardHandleService(mp.Process):
    #
    #     def __init__(self, hkb_input, q):
    #         mp.Process.__init__(self)
    #         self.exit = mp.Event()
    #         self.hkb_input = hkb_input
    #         self.q = q
    #
    #     def run(self):
    #         while not self.exit.is_set():
    #             self.hkb_input.read(False, self.q)
    #
    #     def disconnect(self):
    #         self.exit.set()

    dbname = ''.join(
        ['Prep_Weighing_test_', datetime.now().strftime('%Y%m%d'), '.db'])
    DB.initDB(dbname, settings.DB_PATH)  # CHECK PERMS == ROOT
    system = System(reader, DB.testSession(settings.DB_PATH)['session'])
    logger.debug('Database in use: %s', os.path.join(settings.DB_PATH, dbname))

    Machine = MachineFactory.get_predefined(graph=True, nested=True)
    machine = Machine(
        model=system,
        states=settings.STATES,
        transitions=settings.TRANSITIONS,
        initial='waiting',
        show_auto_transitions=False,
        title="Master",
        show_conditions=True
    )
    if KeyboardHandleService.is_alive():
        system.run()
    # main loop
    while (not killswitch.activated
            and KeyboardHandleService.is_alive()):

        if q.qsize() > 0:
            event = q.get(timeout=1)
            dispatch(json.loads(event))

        time.sleep(.01)

except (queue.Full, Exception) as e:
    logger.critical(e)
    logger.debug(q)
    shutdown(signal.SIGINT)
