#!/usr/bin/env python
import sys
from optparse import OptionParser

# Try to import pyinotify handler, else standard handler
try:
    from watchers.inotify import InotifyWatcher as Watcher
except ImportError:
    from watchers.standard import StandardWatcher as Watcher

def my_callback(data):
    print data

# Run it
if __name__ == '__main__':
    usage = 'usage: %prog [options] path [path ...]'
    parser = OptionParser(usage=usage)
    parser.add_option('-r', '--rescan-freq', dest='rescan_freq', help='rescan frequency in seconds', metavar='SECONDS', default=20)
    parser.add_option('-u', '--update-freq', dest='update_freq', help='update frequnecy in seconds', metavar='SECONDS', default=0)
    parser.add_option('--recursive', action='store_true', dest='recursive')
    (options, args) = parser.parse_args()
 
    if not args:
        print "Need atleast one path (file or directory) to monitor, see --help"
        sys.exit(1)


    settings = {'freq': options.update_freq, 'rescan': options.rescan_freq}

    entities = []
    for arg in args:
        entities.append({'name': args, 'recursive': options.recursive})

    w = Watcher(settings, entities, my_callback)
    w.loop()
