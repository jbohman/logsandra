import pyinotify

class EventHandler(pyinotify.ProcessEvent):
    def my_init(self, callback):
        self.callback = callback

    def process_IN_MODIFY(self, event):
        self.callback(event)

class InotifyWatcher(object):

    def __init__(self, entities, callback, update_freq=0, rescan_freq=20):
        self.update_freq = update_freq
        self.rescan_freq = rescan_freq

        self.entities = entities
        self.callback = lambda x: callback(x.pathname)
        self.wm = pyinotify.WatchManager()

        pyinotify.log.setLevel(50)

    def loop(self):
        notifier = pyinotify.Notifier(self.wm, EventHandler(callback=self.callback), self.update_freq)
        for entity in self.entities:
            # TODO: proc_fun, to add more information about file
            self.wm.add_watch(entity['path'], pyinotify.IN_MODIFY, rec=entity['recursive'])

        notifier.loop()
