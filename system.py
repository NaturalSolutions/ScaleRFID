import os
import logging
from datetime import datetime
import collections
from . import DB
from .RFID import RFIDTag
from .settings import (DIALOGS, NOTIFICATIONS, MODULE_ROOT, RESOLUTIONS)

assert DIALOGS  # noqa: S101  pyflake unused import
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEBUG_TPL_FN = 'state-{}.png'
DEBUG_TPL_DIR = 'debug'
DEBUG_DIR = os.path.join(MODULE_ROOT, DEBUG_TPL_DIR)
os.makedirs(DEBUG_DIR, exist_ok=True)


class System:
    def __init__(self, reader, db, prompt):
        self.reader = reader
        self.db = db
        self.prompt = prompt
        self.current_tag = None
        self.current_specimen = None
        self.start_time = datetime.now()
        self.state_history = collections.deque(maxlen=4)

    @property
    def state(self):
        return self.state_history[-1]

    @state.setter
    def state(self, value):
        self.state_history.append(value)

    def valid_tag(self, *args, **kwargs):
        logger.debug('valid_tag:%s: %s %s', self.state, args, kwargs)

        if (self.current_tag is None
                or not self.current_tag.validate(self.current_tag.code, *args, **kwargs)):  # noqa: E501
            return False

        return True

    def invalid_tag(self, *args, **kwargs):
        logger.debug('invalid_tag:%s: %s %s', self.state, args, kwargs)

        if (self.current_tag is not None
                and self.current_tag.validate(
                    self.current_tag.code, *args, **kwargs)):
            return False

        self.current_tag = None
        return True

    def reader_disconnected(self, *args, **kwargs):
        logger.debug('not_connected:%s: %s %s', self.state, args, kwargs)
        return (self.reader._disconnected_error
                or self.reader._misconfigured_error)

    def reader_read(self, *args, **kwargs):
        logger.debug('on_tagreading_init:%s: %s %s', self.state, args, kwargs)

        self.current_tag = RFIDTag()
        # self.current_tag.code = self.reader.read()
        # FIXME: MOCKING
        from random import choice

        specimens = self.db.query(DB.Session).all()
        random_specimen = choice(specimens)  # noqa: S311
        logger.debug('Randomized ID_RFID %s', random_specimen.ID_RFID)
        self.current_tag.id = str(random_specimen.ID_RFID)
        self.current_tag.code = str(random_specimen.ID_RFID).join(
            [RFIDTag.id_match_start, RFIDTag.id_match_end])

    def query_read(self, *args, **kwargs):
        try:
            query = self.db.query(DB.Session).filter(DB.Session.ID_RFID == self.current_tag.id)  # noqa: E501
            logger.debug('%s %s', query, self.current_tag.id)
            self.current_specimen = self.db\
                .query(DB.Session)\
                .filter(DB.Session.ID_RFID == self.current_tag.id)\
                .one()

            assert self.current_specimen  # noqa: S101
            logger.info('current specimen: %s', self.current_specimen)

        except Exception as e:
            logger.critical('DB related error: %s', e)
            # self.to_querying_unknown('DB related error: {}'.format(e))
            raise

    def query_validate(self, *args, **kwargs):
        if (self.current_specimen is None
                or self.current_specimen.ID_Reneco is None):
            logger.warning('UNREGISTERED_SPECIMEN')
            self.prompt.from_str(
                self.prompt, NOTIFICATIONS, 'UNREGISTERED_SPECIMEN')
            return False

        if self.current_specimen.Position is None:
            logger.warning('NO_POSITION')
            self.prompt.from_str(
                self.prompt, NOTIFICATIONS, 'NO_POSITION')
            return False

        if self.current_specimen.Weight not in (None, 0, 0.0):
            logger.warning('ALREADY_WEIGHED')
            self.prompt.from_str(
                self.prompt, NOTIFICATIONS, 'ALREADY_WEIGHED')
            return False

        return True

    def weight_read(self):
        logger.warning('`system.weight_read` unimplemented.')
        # FIXME: MOCKING
        return 3.1415

    def weight_validate(self):
        logger.warning('`system.weight_validate` unimplemented.')
        # FIXME: MOCKING
        return True

    def prompt_read(self, *args, **kwargs):
        logger.debug('prompt read')
        self.prompt.read()

    def prompt_validate(self, *args, **kwargs):
        return self.prompt.validate()

    def prompt_invalid(self, *args, **kwargs):
        cond = bool(
            self.prompt.enquery != ''
            and self.prompt.choices != dict()
            and self.prompt.answer == '')
        if cond:
            logger.warning('invalid prompt response')
        return cond

    def resolve(self, *args, **kwargs):
        next_state = 'UNDETERMINED'
        method = exit
        if self.prompt.type_ and self.prompt.value_:
            candidates = RESOLUTIONS[self.prompt.value_]
            if len(self.prompt.choices.keys()) > 1 and self.prompt.answer:
                next_state = candidates[int(self.prompt.answer)]
            else:
                next_state = candidates[0]
            method = getattr(self, 'resolve_' + next_state)
        else:
            self.wait()

        context = {
            'specimen': self.current_specimen,
            'tag': self.current_tag.id,
            'history': '↦'.join(self.state_history),
            'prompt': self.prompt.enquery,
            'choices': self.prompt.choices,
            'answer': self.prompt.answer,
            'next_state': next_state,
        }
        logger.debug('Context: %s', context)
        method()

    def save_graph(self, **kwargs):
        import os
        import io

        stream = io.BytesIO()

        # upstream, if not @next, should be fixed soon
        for terminal_node in [
                'tagreading_disconnected', 'tagreading_validated',
                'querying_known', 'querying_unknown',
                'weighing_rejected', 'weighing_validated',
                'updating_failed', 'updating_committed',
                'prompting_resolved']:
            self.get_graph(**kwargs).get_node(terminal_node)\
                                    .attr.update(peripheries=2)

        self.get_graph(**kwargs).draw(stream, format='png', prog='dot')
        with open(
                os.path.join(
                    DEBUG_DIR,
                    DEBUG_TPL_FN.format(datetime.now().isoformat())),
                'wb+') as fp:
            fp.write(stream.getvalue())

    def show(self):
        import os
        import glob

        myimages = sorted(
            glob.glob(os.path.join(DEBUG_DIR, DEBUG_TPL_FN.format('*'))),
            key=os.path.getctime,
            reverse=True)
        lower_time_bound = self.start_time.timestamp()
        dts = datetime.fromtimestamp
        myimages = filter(
            lambda f: dts(os.path.getctime(f)) > dts(lower_time_bound),
            myimages)
        myimages = sorted(myimages, reverse=True)
        logger.warning('Generating poor man\'s statechart timeline')

        import matplotlib.pyplot as plt
        import matplotlib.image as mpltImage
        from matplotlib import animation

        logging.getLogger('matplotlib').setLevel(logging.WARNING)  # pfff
        size = (1920, 1080)
        fig = plt.figure()
        fig.set_size_inches(size[0] / 100, size[1] / 100)
        ax = fig.add_axes([0, 0, 1, 1], frameon=False, aspect=1)
        ax.set_xticks([])
        ax.set_yticks([])

        assembled = []
        for i in myimages:
            img = mpltImage.imread(i)
            computed = plt.imshow(img)
            assembled.append([computed])

        my_anim = animation.ArtistAnimation(
            fig, assembled, interval=1000, blit=False, repeat_delay=1000)
        assert my_anim  # noqa: S101
        plt.show()
        # my_anim.save(os.path.join(MODULE_ROOT, 'debug', 'animation.mp4')

        # fname = os.path.join(
        #     DEBUG_DIR, 'states-{}.gif'.format(datetime.now().isoformat()))
        # cmd = ' '.join(['/usr/bin/convert', '-delay', '10', '-loop', '0',
        #                 *myimages, fname])
        # os.system(cmd)  # noqa: S605
