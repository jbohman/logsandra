# Try to import pyinotify handler, else standard handler
#try:
#    from inotify import InotifyWatcher as Watcher
#except ImportError:
#    from standard import StandardWatcher as Watcher

from standard import StandardWatcher as Watcher
