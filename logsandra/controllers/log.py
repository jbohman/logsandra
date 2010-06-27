import logging
import datetime
import time
import pycassa
import struct

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from logsandra.lib.base import BaseController, render
from logsandra import config
from logsandra.utils.model import Cassandra

log = logging.getLogger(__name__)


class LogController(BaseController):

    def index(self):
        return render('/log_index.html')

    def view(self):
        date_from = request.GET['date_from']
        date_to = request.GET['date_to']
        status = request.GET['status']
        search_keyword = request.GET['search_keyword']

        keyword = status
        if search_keyword:
            keyword = search_keyword

        current_prev = None
        current_next = None
        if 'next' in request.GET:
            current_next = long(request.GET['next'])

        if 'prev' in request.GET:
            current_prev = long(request.GET['prev'])

        if date_from:
            try:
                date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                redirect(url(controller='log', action='error'))
        else:
            date_from = ''

        if date_to:
            try:
                date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                redirect(url(controller='log', action='error'))
        else:
            date_to = ''
        
        # TODO: Move this to a final that could be used by other controllers
        # and make sure it uses the config file
        client = Cassandra('', 'localhost', 9160, 5)

        if current_next:
            entries, last, first = client.get_entries_by_keyword(keyword,
                    date_from, date_to, action_next=current_next)
        elif current_prev:
            entries, last, first = client.get_entries_by_keyword(keyword,
                    date_from, date_to, action_prev=current_prev)
        else:
            entries, last, first = client.get_entries_by_keyword(keyword,
                    date_from, date_to) 

        c.entries = entries

        if last:
            c.next_url = url(controller='log', action='view',
                    search_keyword=request.GET['search_keyword'],
                    status=request.GET['status'],
                    date_from=request.GET['date_from'],
                    date_to=request.GET['date_to'], next=last) 

        if first:
            c.prev_url = url(controller='log', action='view', 
                    search_keyword=request.GET['search_keyword'],
                    status=request.GET['status'],
                    date_from=request.GET['date_from'],
                    date_to=request.GET['date_to'], prev=first) 

        return render('/log_view.html')

    def error(self):
        return 'Error, could not parse date'
