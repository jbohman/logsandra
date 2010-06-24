import os
import os.path
import time

class StandardWatcher(object):

    def __init__(self, entities, callback, update_freq=10, rescan_freq=20):
        self.update_freq = update_freq
        self.rescan_freq = rescan_freq

        self.entities = entities
        self.callback = callback

        self.files = {}

        for filename, entity in self._find_files_generator():
            self.files[filename] = {'mtime': self._mtime(filename), 'data': entity}

        self._last_rescan_time = time.time()

    def loop(self):
        while True:
            current_time = time.time()
            if (current_time - self._last_rescan_time) > self.rescan_freq:
                self._last_rescan_time = self._rescan()

            reference_time = time.time()
            for filename, data in self.files.iteritems():
                new_mtime = self._mtime(filename)
                if new_mtime > data['mtime']:
                    self.files[filename]['mtime'] = new_mtime
                    data = self.files[filename]['data']
                    data['source'] = filename
                    self.callback(filename, data)

            if self.update_freq > 0:
                current_time = time.time()
                sleep = self.update_freq - (current_time - reference_time)
                if sleep > 0:
                    time.sleep(sleep)

    def _find_files_generator(self):
        for entity in self.entities:
            # Is directory
            if os.path.isdir(entity['name']):
                if entity['recursive']:
                    for path in os.walk(entity['name']):
                        if path[2]:
                            for filename in path[2]:
                                filename = os.path.join(os.path.abspath(path[0]), filename)
                                yield filename, entity
                else:
                    for filename in os.listdir(entity['name']):
                        filename = os.path.abspath(entity['name']) + '/' + filename
                        if os.path.isfile(filename):
                            yield filename, entity
            # Is file
            else:
                if os.path.exists(os.path.expanduser(entity['name'])):
                    filename = os.path.abspath(os.path.expanduser(entity['name']))
                    yield filename, entity
                else:
                    raise Error('Invalid path, cannot monitor it')

    def _rescan(self):
        tempfiles = {}
        for filename, entity in self._find_files_generator():
            if filename not in self.files:
                self.files[filename] = {'mtime': self._mtime(filename), 'data': entity}
            tempfiles[filename] = 0

        result = set(self.files).difference(set(tempfiles)) 
        for element in result:
            del self.files[element]

        return time.time()


    def _mtime(self, filename):
        try:
            return os.stat(filename).st_mtime
        except os.error:
            return False
