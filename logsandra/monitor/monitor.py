#!/usr/bin/env python
import sys
import os.path
from optparse import OptionParser

# Try to import pyinotify handler, else standard handler
try:
    from watchers.inotify import InotifyWatcher as Watcher
except ImportError:
    from watchers.standard import StandardWatcher as Watcher


class Reader(object):

    def __init__(self, tail=False):
        self.tail = tail
        self.seek_data = {}

    def callback(self, filename):
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
                print line.strip()

            self.seek_data[filename] = file_handler.tell()
            file_handler.close()

        except IOError:
            pass

# Run it
if __name__ == '__main__':
    usage = 'usage: %prog [options] path [path ...]'
    parser = OptionParser(usage=usage)
    parser.add_option('-r', '--rescan-freq', dest='rescan_freq', help='rescan frequency in seconds', metavar='SECONDS', default=20)
    parser.add_option('-u', '--update-freq', dest='update_freq', help='update frequnecy in seconds', metavar='SECONDS', default=0)
    parser.add_option('-t', '--tail', action='store_true', dest='tail', help='start reading from the bottom only', default=False)
    parser.add_option('--recursive', action='store_true', dest='recursive')
    (options, args) = parser.parse_args()
 
    if not args:
        print "Need atleast one path (file or directory) to monitor, see --help"
        sys.exit(1)

    settings = {'freq': options.update_freq, 'rescan': options.rescan_freq}

    entities = []
    for arg in args:
        entities.append({'name': args, 'recursive': options.recursive})

    r = Reader(options.tail)
    w = Watcher(settings, entities, r.callback)
    w.loop()
