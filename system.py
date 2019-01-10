import logging

from . import DB
from .RFID import RFIDTag

logger = logging.getLogger()
current_tag = None
current_specimen = None


class System:
    def __init__(self, reader, db):
        self.reader = reader
        self.db = db

    def valid_tag(self, *args, **kwargs):
        logger.debug('valid_tag:%s: %s %s', self.state, args, kwargs)

        if current_tag is None or not current_tag.validate(*args, **kwargs):
            return False

        return True

    def invalid_tag(self, *args, **kwargs):
        global current_tag

        logger.debug('invalid_tag:%s: %s %s', self.state, args, kwargs)

        if current_tag is not None and current_tag.validate(*args, **kwargs):
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
            logger.info('%s', current_specimen)

            if current_specimen is None or current_specimen.ID_Reneco is None:
                logger.warning('Bird Chip Not In Database')
                self.to_query_unknown('Bird Chip Not In Database')

            if current_specimen.Position is None:
                logger.warning('BIRD POSITION NOT IN DATABASE')
                self.to_query_unknown('BIRD POSITION NOT IN DATABASE')

            if current_specimen.Weight not in (None, 0, 0.0):
                logger.warning('Bird Already Weighed')
                self.to_query_unknown('Bird Already Weighed')

        except Exception as e:
            logger.critical('DB related error: %s', e)
            self.to_query_unknown('DB related error: {}'.format(e))

    def acknowledgement(self):
        self.acknowledge()

    # def show_graph(self, *args, **kwargs):
    #     stream = io.BytesIO()
    #     for terminal_node in [
    #             'tagreading_disconnected', 'tagreading_validated',
    #             'querying_known', 'querying_unknown',
    #             'weighing_rejected', 'weighing_validated',
    #             'updating_failed', 'updating_committed',
    #             'prompting_resolved']:
    #         self.get_graph(*args, **kwargs).get_node(terminal_node)\
    #                                        .attr.update(peripheries=2)
    #
    #     self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
    #     display(Image(stream.getvalue()))
