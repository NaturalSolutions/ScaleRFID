from . import DB
from .RFID import RFIDTag
from .prompt import Prompt
from .settings import logger

current_tag = None
current_specimen = None


class System:
    def __init__(self, reader, db):
        self.reader = reader
        self.db = db
        self.prompt = None

    def valid_tag(self, *args, **kwargs):
        logger.debug('valid_tag:%s: %s %s', self.state, args, kwargs)

        if (current_tag is None
                or not current_tag.validate(current_tag.code, *args, **kwargs)):  # noqa: E501
            return False

        return True

    def invalid_tag(self, *args, **kwargs):
        global current_tag

        logger.debug('invalid_tag:%s: %s %s', self.state, args, kwargs)

        if (current_tag is not None
                and current_tag.validate(current_tag.code, *args, **kwargs)):
            return False

        current_tag = None
        return True

    def reader_disconnected(self, *args, **kwargs):
        logger.debug('not_connected:%s: %s %s', self.state, args, kwargs)
        return (True
                if self.reader._disconnected_error
                or self.reader._misconfigured_error
                else False)

    def reader_read(self, *args, **kwargs):
        global current_tag

        logger.debug('on_tagreading_init:%s: %s %s', self.state, args, kwargs)

        current_tag = RFIDTag()
        current_tag.code = self.reader.read()

    def query_read(self, *args, **kwargs):
        global current_specimen

        try:
            current_specimen = self.db\
                .query(DB.Session)\
                .filter(DB.Session.ID_RFID == current_tag.id)\
                .first()
            logger.info('current specimen: %s', current_specimen)

        except Exception as e:
            logger.critical('DB related error: %s', e)
            # self.to_querying_unknown('DB related error: {}'.format(e))

    def query_validate(self, *args, **kwargs):
        if (current_specimen is None
                or current_specimen.ID_Reneco is None):
            logger.warning('UNREGISTERED_SPECIMEN')
            return False

        if current_specimen.Position is None:
            logger.warning('NO_POSITION')
            return False

        if current_specimen.Weight not in (None, 0, 0.0):
            logger.warning('ALREADY_WEIGHED')
            return False

        return True

    def weight_read(self):
        logger.warning('`system.weight_read` unimplemented.')

    def weight_validate(self):
        logger.warning('`system.weight_validate` unimplemented.')
        return True

    def prompt_init(self):
        self.prompt = Prompt(msg='Pouët\n1 - OK\n2 - NOK')

    def prompt_read(self):
        self.prompt.read()

    def prompt_validate(self):
        return self.prompt.validate()

    def show_graph(self, *args, **kwargs):
        import os
        import io
        from datetime import datetime as dt

        from . import settings

        stream = io.BytesIO()
        for terminal_node in [
                'tagreading_disconnected', 'tagreading_validated',
                'querying_known', 'querying_unknown',
                'weighing_rejected', 'weighing_validated',
                'updating_failed', 'updating_committed',
                'prompting_resolved']:
            self.get_graph(*args, **kwargs).get_node(terminal_node)\
                                           .attr.update(peripheries=2)

        self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
        with open(os.path.join(settings.MODULE_ROOT, 'state-{}.png'.format(dt.now().isoformat())), 'wb+') as fp:  # noqa: E501
            fp.write(stream.getvalue())
