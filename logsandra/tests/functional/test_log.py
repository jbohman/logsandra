from logsandra.tests import *

class TestLogController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='log', action='index'))
        # Test response...
