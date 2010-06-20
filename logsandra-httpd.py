#!/usr/bin/env python
"""
Logsandra http daemon
"""
# Global imports
import sys
import os
import optparse
import socket
import logging
from cherrypy import wsgiserver
from paste.deploy import loadapp

# Local imports
from logsandra import utils
from logsandra.utils.daemon import Daemon

class Application(Daemon):

    def run(self):
        logger = logging.getLogger('logsandra.httpd')

        wsgi_app = loadapp('config:%s' % self.settings.config_file, relative_to=self.settings.working_directory)
        wsgi_app.config['logsandra'] = {'cassandra_address': 'localhost', 'cassandra_port': 9160, 'cassandra_timeout': 5}
        server = wsgiserver.CherryPyWSGIServer((self.settings.host, self.settings.port), wsgiserver.WSGIPathInfoDispatcher({'/': wsgi_app}))
        try:
            logger.debug('Starting server')
            server.start()
        except socket.error:
            logger.error('Address already in use')
        except KeyboardInterrupt:
            logger.debug('Stopping server')
            server.stop()


if __name__ == '__main__':

    default_working_directory = os.curdir

    usage = 'usage: %prog [options] start|stop|restart'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--config', dest='config_file', metavar='FILE', default='development.ini')
    parser.add_option('--working-directory', dest='working_directory', metavar='DIRECTORY', default=default_working_directory)
    parser.add_option('--pid', dest='pid_file', metavar='FILE', default=os.path.join(default_working_directory, 'logsandra-httpd.pid'))
    parser.add_option('--application-data-directory', dest='application_data_directory', default=utils.application_data_directory('logsandra'))
    parser.add_option('--host', dest='host', metavar='HOST', default='0.0.0.0')
    parser.add_option('--port', dest='port', metavar='PORT', type='int', default=5000)
    (options, args) = parser.parse_args()

    if not os.path.isdir(options.application_data_directory):
        os.makedirs(options.application_data_directory)

    logfile = os.path.join(options.application_data_directory, 'logsandra.log')
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format="%(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] [%(threadName)s] %(message)s")

    application = Application(options.pid_file, working_directory=options.working_directory, stdout=logfile, stderr=logfile)
    application.settings = options

    if len(args) == 1:
        if args[0] == 'start':
            application.start()
        elif args[0] == 'stop':
            application.stop()
        elif args[0] == 'restart':
            application.restart()
        else:
            print parser.get_usage()
            sys.exit(2)
        
        sys.exit(0)
    else:
        print parser.get_usage()
        sys.exit(2)
