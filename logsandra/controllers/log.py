import logging
import datetime
import time
import pycassa
import struct
from cassandra.ttypes import NotFoundException

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from logsandra.lib.base import BaseController, render
from logsandra import config

log = logging.getLogger(__name__)

class LogController(BaseController):

    def index(self):
        return render('/log_index.html')

    def view(self):
        date_from = request.GET['date_from']
        date_to = request.GET['date_to']
        status = request.GET['status']

        if date_from and date_to:
            try:
                date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
                date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                redirect(url(controller='log', action='error'))
        else:
            date_from = None
            date_to = None
        
        # TODO: Move this to a final that could be used by other controllers and make sure it uses the config file
        connect_string = '%s:%s' % ('localhost', 9160)
        client = pycassa.connect([connect_string], timeout=5)

        # Column families
        entries = pycassa.ColumnFamily(client, 'logsandra', 'entries')
        by_date = pycassa.ColumnFamily(client, 'logsandra', 'by_date')
        by_date_data = pycassa.ColumnFamily(client, 'logsandra', 'by_date_data')

        long_struct = struct.Struct('>q')

        c.entries = []
        try:
            if date_from and date_to:
                result = by_date_data.get(str(status), column_start=long_struct.pack(int(time.mktime(date_from.timetuple()))), 
                            column_finish=long_struct.pack(int(time.mktime(date_to.timetuple()))))
            else:
                result = by_date_data.get(str(status))

            for elem in result.itervalues():
                c.entries.append(elem.strip())
        except NotFoundException:
            pass

        return render('/log_view.html')

    def error(self):
        return 'Error, could not parse date'
