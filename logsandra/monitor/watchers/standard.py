import os
import os.path
import time

class StandardWatcher(object):

    def __init__(self, settings, entities, callback):
        self.settings = settings
        self.entities = entities
        self.callback = callback
        self.files = {}

        for filename in self._find_files_generator():
            self.files[filename] = self._mtime(filename)

        self._last_rescan_time = time.time()

    def loop(self):
        while True:
            current_time = time.time()
            if (current_time - self._last_rescan_time) > self.settings['rescan']:
                self._last_rescan_time = self._rescan()

            reference_time = time.time()
            for filename, mtime in self.files.iteritems():
                new_mtime = self._mtime(filename)
                if new_mtime > mtime:
                    self.files[filename] = new_mtime
                    self.callback(filename)

            if self.settings['freq'] > 0:
                current_time = time.time()
                sleep = self.settings['freq'] - (current_time - reference_time)
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
                                yield filename
                else:
                    for filename in os.listdir(entity['name']):
                        filename = os.path.abspath(entity['name']) + '/' + filename
                        if os.path.isfile(filename):
                            yield filename
            # Is file
            else:
                filename = os.path.join(os.path.abspath(entity['name']), entity['name'])
                yield filename

    def _rescan(self):
        tempfiles = {}
        for filename in self._find_files_generator():
            if filename not in self.files:
                self.files[filename] = self._mtime(filename)
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


if __name__ == '__main__':
    def callback(x):
        print x

    sw = StandardWatcher({'freq': 1, 'rescan': 10}, [{'name': '.', 'recursive': False}], callback)
    sw.loop()
