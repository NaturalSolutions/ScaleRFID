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

from transitions.extensions import MachineFactory

from . import (
    settings,
    hkb_input,
    KillSwitch,
    DB
)
from .event_dispatcher import Event, EventDispatcher
from .RFID import RFIDReader  # , RFIDTag
from .system import System

logger = settings.logger
mp.log_to_stderr(10)
dispatcher = EventDispatcher()
hkb4 = hkb_input.HKB4Device(settings.HKB4_PORT)
killswitch = KillSwitch.KillSwitch(key_code=30, threshold=.500)
reader = RFIDReader(settings.RFID_READER_PORT)
DB.initDB(
    ''.join(['Prep_Weighing_test_', datetime.now().strftime('%Y%m%d'), '.db']),
    settings.DB_PATH)
system = System(reader, DB.testSession(settings.DB_PATH)['session'])

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
    # class KeyboardHandleService(multiprocessing.Process):
    #
    # def __init__(self, hkb_input, q):
    #     multiprocessing.Process.__init__(self)
    #     self.exit = multiprocessing.Event()
    #
    # def run(self):
    #     while not self.exit.is_set():
    #         hkb_input.read(False, q)
    #
    # def disconnect(self):
    #     self.exit.set()

    states = [
        'waiting',
        'running',
        {
            'name': 'tagreading',
            'initial': 'init',
            'children': ['init', 'read', 'disconnected', 'validated']
        }, {
            'name': 'prompting',
            'initial': 'init',
            'children': ['init', 'read', 'resolved']
        }, {
            'name': 'querying',
            'initial': 'init',
            'children': ['init', 'read', 'known', 'unknown']
        }, {
            'name': 'weighing',
            'initial': 'init',
            'children': ['init', 'read', 'rejected', 'validated']
        }, {
            'name': 'updating',
            'initial': 'init',
            'children': ['init', 'read', 'failed', 'committed']
        }
    ]

    transitions = [
        {'trigger': 'run', 'source': 'waiting', 'dest': 'running', 'after': 'collect_tag'},  # noqa: E501
        ['wait', ['running', 'prompting_resolved'], 'waiting'],
        ['init', ['tagreading'], 'tagreading_init'],
        ['init', ['querying', ], 'querying_init'],
        ['init', ['weighing', 'prompt_resolved'], 'weighing_init'],
        ['init', ['updating'], 'updating_init'],
        ['init', ['prompting', ], 'prompting_init'],
        # check database update, create .CSV
        {'trigger': 'collect_tag', 'source': 'running', 'dest': 'tagreading', 'after': 'read_tag'},  # noqa: E501
        {'trigger': 'read_tag', 'source': 'tagreading_init', 'dest': 'tagreading_read', 'before': 'reader_read', 'after': 'validate_tag'},  # noqa: E501
        {'trigger': 'validate_tag', 'source': 'tagreading_read', 'dest': 'tagreading_disconnected', 'after': 'acknowledge'},  # noqa: E501
        {'trigger': 'validate_tag', 'source': 'tagreading_read', 'dest': 'tagreading_init', 'conditions': 'invalid_tag'},  # noqa: E501
        {'trigger': 'validate_tag', 'source': 'tagreading_read', 'dest': 'tagreading_validated', 'conditions': 'valid_tag', 'unless': 'reader_disconnected', 'after': 'collect_query'},  # noqa: E501
        {'trigger': 'collect_query', 'source': 'tagreading_validated', 'dest': 'querying', 'after': 'read_query'},  # noqa: E501
        {'trigger': 'read_query', 'source': 'querying_init', 'dest': 'querying_read', 'before': 'query_read', 'after': 'validate_query'},  # noqa: E501
        {'trigger': 'validate_query', 'source': 'querying_read', 'dest': 'querying_unknown', 'after': 'acknowledge'},  # unregistered specimen or unknown specimen position  # noqa: E501
        {'trigger': 'validate_query', 'source': 'querying_read', 'dest': 'querying_known', 'after': 'collect_weighing'},  # registered specimen and known specimen position  # noqa: E501
        # ['validate_query', 'querying_read', 'querying_init'],  # some db related error  # noqa: E501
        {'trigger': 'collect_weighing', 'source': 'querying_known', 'dest': 'weighing'},  # valid chip and known specimen and known position and not yet weighed today  # noqa: E501
        {'trigger': 'read_weight', 'source': 'weighing_init', 'dest': 'weighing_read', 'before': 'weight_read', 'after': 'validate_weight'},  # noqa: E501
        ['collect', 'weighing_validated', 'updating'],
        ['read', 'updating_init', 'updating_read'],
        ['read', 'prompting_init', 'prompting_read'],
        ['validate', 'weighing_read', 'weighing_validated'],  # normal specimen weight  # noqa: E501
        {'trigger': 'validate', 'source': 'weighing_read', 'dest': 'weighing_rejected', 'after': 'acknowledge'},  # inconsistent or pathological weight  # noqa: E501
        ['validate', 'weighing_read', 'weighing_init'],  # disconnected rfidreader  # noqa: E501
        ['validate', 'updating_read', 'updating_committed'],  # database transaction committed  # noqa: E501
        {'trigger': 'validate', 'source': 'updating_read', 'dest': 'updating_failed', 'after': 'acknowledge'},  # db record update error  # noqa: E501
        ['validate', 'updating_read', 'updating_init'],
        ['validate', 'prompting_read', 'prompting_resolved'],  # confirmed pathological weight or reconnected rdfidreader or acknowledged (outdated db or specimen unknown position or unregistered specimen or specimen invalid rf chip id)  # noqa: E501
        ['acknowledge', ['tagreading_disconnected', 'querying_unknown', 'weighing_rejected', 'updating_failed', 'updating_committed'], 'prompting'],  # noqa: E501
        # collect operator's comments
    ]
    Machine = MachineFactory.get_predefined(graph=False, nested=True)
    machine = Machine(
        model=system,
        states=states,
        transitions=transitions,
        initial='waiting',
        # show_auto_transitions=False,
        # title="Master",
        # show_conditions=True
    )
    # main loop
    system.run()
    while not killswitch.activated:

        if q.qsize() > 0:
            event = q.get(timeout=1)
            dispatch(json.loads(event))

        time.sleep(.01)

except (queue.Full, Exception) as e:
    logger.critical(e)
    logger.debug(q)
    shutdown(127)
