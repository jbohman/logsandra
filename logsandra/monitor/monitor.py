# Global imports
import os.path
import time
import uuid
import struct
import pycassa
import logging
import imp

# Local imports
from logsandra.monitor.watchers import Watcher
from logsandra.monitor.parsers.clf import ClfParser
from logsandra.model import CassandraClient, LogEntry


class Monitor(object):

    def __init__(self, settings, tail=False):
        self.logger = logging.getLogger('logsandra.monitord')
        self.settings = settings
        self.client = CassandraClient(self.settings['ident'], self.settings['cassandra_address'], self.settings['cassandra_port'], self.settings['cassandra_timeout'])

        self.tail = tail
        self.seek_position = {}

        self.parsers = {}
        log_entry = LogEntry(self.client)
        parsers_path = os.path.join(os.path.dirname(imp.find_module('logsandra/monitor/')[1]), 'parsers/')
        parsers_files = [filename[:-3] for filename in os.listdir(parsers_path) if filename.endswith('.py') and not filename.startswith('__')]
        parsers_temp = __import__('logsandra.monitor.parsers', globals(), locals(), parsers_files, -1)
        for filename in parsers_files:
            module = getattr(parsers_temp, filename)
            classname = '%sParser' % (filename.capitalize())
            self.parsers[filename] = getattr(module, classname)(log_entry)

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
            if filename in self.seek_position:
                file_handler.seek(self.seek_position[filename])
            else:
                if self.tail:
                    file_handler.seek(0, os.SEEK_END)

            for line in file_handler:
                line = line.strip()

                result = self.parsers[data['parser']['name']].parse(line, data['source'], data['parser'])
                if result:
                    self.logger.debug('Parsed line: %s' % line)
                else:
                    self.logger.error('Failed to parse line: %s' % line)

            # TODO: Persist seek_position
            self.seek_position[filename] = file_handler.tell()
            file_handler.close()

        except IOError:
            pass
