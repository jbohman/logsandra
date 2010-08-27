import logging

from pylons import request, response, session, tmpl_context as c, url, config
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect

from logsandra.lib.base import BaseController, render
from logsandra.model import LogEntry, CassandraClient

log = logging.getLogger(__name__)

class GraphController(BaseController):

    def index(self):
        return render('/graph_index.html')

    def view(self):
        c.keyword = request.GET['keyword']
        return render('/graph_view.html')

    @jsonify
    def ajax(self):
        cassandra_client = CassandraClient(config['ident'], config['cassandra_host'], config['cassandra_port'], config['cassandra_timeout'])
        log_entries = LogEntry(cassandra_client)

        keyword = request.GET['keyword']
        column_next = ''
        if 'next' in request.GET and request.GET['next']:
            column_next = long(request.GET['next'])

        return {'result': log_entries.get_date_count(keyword, column_next=column_next)}
        
    def error(self):
        return 'Error, could not parse date'
