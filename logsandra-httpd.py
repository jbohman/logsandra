#!/usr/bin/env python
"""
Logsandra http daemon
"""
import sys
import os
import optparse
import socket
import logging
from cherrypy import wsgiserver
from paste.deploy import loadapp

from logsandra import utils
from logsandra.utils.daemon import Daemon
from logsandra.utils import config

class Application(Daemon):

    def run(self):
        wsgi_app = loadapp('config:%s' % self.config['httpd_config'], relative_to=self.config['httpd_working_directory'], global_conf={
                'cassandra_address': self.config['cassandra_address'], 
                'cassandra_port': self.config['cassandra_port'], 
                'cassandra_timeout': self.config['cassandra_timeout'],
                'ident': self.config['ident']})
        server = wsgiserver.CherryPyWSGIServer((self.config['httpd_host'], int(self.config['httpd_port'])), wsgiserver.WSGIPathInfoDispatcher({'/': wsgi_app}))
        try:
            self.logger.debug('Starting httpd server at %s:%s' % (self.config['httpd_host'], self.config['httpd_port']))
            server.start()
        except socket.error:
            self.logger.error('Address already in use: %s:%s' % (self.config['httpd_host'], self.config['httpd_port']))
            server.stop()
        except KeyboardInterrupt:
            self.logger.error('Httpd server stopped by KeyboardInterrupt')
            server.stop()


if __name__ == '__main__':

    default_working_directory = os.curdir
    default_config_file = os.path.join(default_working_directory, 'logsandra.yaml')

    usage = 'usage: %prog [options] start|stop|restart'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--config', dest='config_file', metavar='FILE', default=default_config_file)
    parser.add_option('--working-directory', dest='working_directory', metavar='DIRECTORY', default=default_working_directory)
    parser.add_option('--pid', dest='pid_file', metavar='FILE', default=os.path.join(default_working_directory, 'logsandra-httpd.pid'))
    parser.add_option('--application-data-directory', dest='application_data_directory', default=utils.application_data_directory('logsandra'))
    parser.add_option('--host', dest='host', metavar='HOST')
    parser.add_option('--port', dest='port', metavar='PORT', type='int')
    (options, args) = parser.parse_args()

    if not os.path.isdir(options.application_data_directory):
        os.makedirs(options.application_data_directory)

    logfile = os.path.join(options.application_data_directory, 'logsandra.log')
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format="%(asctime)s %(levelname)-5.5s [%(name)s] [%(threadName)s] %(message)s")
    logger = logging.getLogger('logsandra.httpd')

    application = Application(options.pid_file, working_directory=options.working_directory, stdout=logfile, stderr=logfile)
    application.config = config.parse(options.config_file)
    application.config['httpd_working_directory'] = options.working_directory
    application.logger = logger

    if options.host:
        application.config['httpd_host'] = options.host

    if options.port:
        application.config['httpd_port'] = options.port

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
