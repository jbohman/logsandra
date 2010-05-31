import pyinotify

class EventHandler(pyinotify.ProcessEvent):
    def my_init(self, callback):
        self.callback = callback

    def process_IN_MODIFY(self, event):
        self.callback(event)

class InotifyWatcher(object):

    def __init__(self, settings, entities, callback):
        self.settings = settings
        self.entities = entities
        self.callback = lambda x: callback(x.pathname)
        self.wm = pyinotify.WatchManager()

        pyinotify.log.setLevel(50)

    def loop(self):
        notifier = pyinotify.Notifier(self.wm, EventHandler(callback=self.callback), self.settings['freq'])
        for entity in self.entities:
            self.wm.add_watch(entity['name'], pyinotify.IN_MODIFY, rec=entity['recursive'])

        notifier.loop()
