# Global imports
import os.path
import time
import uuid
import struct
import pycassa


from watchers import Watcher
from parsers.clf import ClfParser


class Monitor(object):

    def __init__(self, settings, tail=False):
        self.settings = settings

        self.tail = tail
        self.seek_data = {}
        self.parser = {}

    def run(self):
        # Connect to cassandra
        connect_string = '%s:%s' % (self.settings['cassandra_address'], self.settings['cassandra_port'])
        self.client = pycassa.connect([connect_string], timeout=self.settings['cassandra_timeout'])

        # Column families
        self.entries = pycassa.ColumnFamily(self.client, 'logsandra', 'entries')
        self.by_date = pycassa.ColumnFamily(self.client, 'logsandra', 'by_date')
        self.by_date_data = pycassa.ColumnFamily(self.client, 'logsandra', 'by_date_data')

        # Struct
        self.long_struct = struct.Struct('>q')

        # Start watcher (inf loop)
        self.watcher = Watcher(self.settings['paths'], self.callback)
        self.watcher.loop()

    def _to_long(self, data):
        return self.long_struct.pack(data)

    def _from_long(self, data):
        return self.long_struct.unpack(data)

    def callback(self, filename, data):
        if os.path.basename(filename).startswith('.'):
            return False

        try:
            file_handler = open(filename, 'rb')
            if filename in self.seek_data:
                file_handler.seek(self.seek_data[filename])
            else:
                if self.tail:
                    file_handler.seek(0, os.SEEK_END)

            for line in file_handler:
                line = line.strip()

                if filename not in self.parser:
                    self.parser[filename] = ClfParser(data['format'])

                result = self.parser[filename].parse_line(line)

                # TODO: Should move this to every individual parser
                key = uuid.uuid4()
                self.entries.insert(key.bytes, {'ident': self.settings['ident'], 'entry': line})

                if 'status' in result:
                    # TODO: is this really how pycassa should be used?
                    self.by_date.insert(str(result['status']), {self._to_long(int(time.mktime(result['time'].timetuple()))): str(key)})
                    self.by_date_data.insert(str(result['status']), {self._to_long(int(time.mktime(result['time'].timetuple()))): str(line)})

                print result

            self.seek_data[filename] = file_handler.tell()
            file_handler.close()

        except IOError:
            pass
