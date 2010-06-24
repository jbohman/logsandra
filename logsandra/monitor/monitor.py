# Global imports
import os.path
import time
import uuid
import struct
import pycassa
import logging

# Local imports
from logsandra.monitor.watchers import Watcher
from logsandra.monitor.parsers.clf import ClfParser
from logsandra.utils.model import Cassandra


class Monitor(object):

    def __init__(self, settings, tail=False):
        self.logger = logging.getLogger('logsandra.monitord')
        self.settings = settings
        self.client = Cassandra(self.settings['ident'], self.settings['cassandra_address'], self.settings['cassandra_port'], self.settings['cassandra_timeout'])

        self.tail = tail
        self.seek_data = {}
        self.parsers = {'clf': ClfParser(self.client)}

    def run(self):

        self.logger.debug('Starting watcher')
        self.watcher = Watcher(self.settings['paths'], self.callback)
        self.watcher.loop()

    def callback(self, filename, data):
        if os.path.basename(filename).startswith('.'):
            return False

        self.logger.debug('A change occurred in file %s with data %s' % (filename, data))

        try:
            file_handler = open(filename, 'rb')
            if filename in self.seek_data:
                file_handler.seek(self.seek_data[filename])
            else:
                if self.tail:
                    file_handler.seek(0, os.SEEK_END)

            for line in file_handler:
                line = line.strip()

                result = self.parsers[data['parser']].parse(line, data)
                if result:
                    self.logger.debug('Parsed line: %s' % line)
                else:
                    self.logger.error('Failed to parse line: %s' % line)

            # TODO: Persist seek_data
            self.seek_data[filename] = file_handler.tell()
            file_handler.close()

        except IOError:
            pass
