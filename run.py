#!/usr/bin/env python
# Global imports
import sys
import os
import optparse
import time
import multiprocessing
import logging

from cherrypy import wsgiserver
from paste.deploy import loadapp

# Local imports
from logsandra import monitor, config, utils
from logsandra.utils.daemon import Daemon


class Application(Daemon):

    def monitor(self):
        m = monitor.Monitor(self.settings, False)
        m.run()

    # TODO: setup application here, monitor + pylon webservice
    def run(self):

        # Setup logging
        logging.basicConfig(filename=self.settings['logfile_name'], level=logging.DEBUG)

        # Test to see if settings is present
        if not hasattr(self, 'settings'):
            print 'No settings, exiting...'
            sys.exit(1)

        # Start monitor process
        print 'Starting monitor service...'
        self.monitor_process = multiprocessing.Process(target=self.monitor)
        self.monitor_process.start()

        # Start web process
        print 'Starting web service...' 
        wsgi_app = loadapp('config:/home/tote/coding/cassandra/logsandra/development.ini')
        d = wsgiserver.WSGIPathInfoDispatcher({'/': wsgi_app})
        server = wsgiserver.CherryPyWSGIServer((self.settings['webservice_address'], int(self.settings['webservice_port'])), d)
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()


if __name__ == '__main__':

    default_working_directory = os.curdir
    default_path = os.path.split(os.path.dirname(__file__))[0]
    default_config_file = os.path.join(default_path, 'config.yaml')

    usage = 'usage: %prog [options] start|stop|restart'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--config-file', dest='config_file', metavar='FILE', default=default_config_file)
    parser.add_option('--working-directory', dest='working_directory', metavar='DIRECTORY', default=default_working_directory)
    parser.add_option('--pid-file', dest='pid_file', metavar='FILE', default='/tmp/logsandra.pid')
    parser.add_option('--application-data-directory', dest='application_data_directory', default=utils.application_data_directory('logsandra'))
    (options, args) = parser.parse_args()

    if not os.path.isdir(options.application_data_directory):
        os.makedirs(options.application_data_directory)

    output_file = os.path.join(options.application_data_directory, 'logsandra.log')

    application = Application(options.pid_file, stdout=output_file, stderr=output_file)
    application.settings = config.parse(options.config_file)
    application.settings['application_data_directory'] = options.application_data_directory
    application.settings['logfile_name'] = output_file

    if len(args) == 1:
        if args[0] == 'start':
            application.start()
        elif args[0] == 'stop':
            application.stop()
        elif args[0] == 'restart':
            application.restart()
        else:
            print 'Unknown command'
            sys.exit(2)
        
        sys.exit(0)
    else:
        application.run()
        #print parser.get_usage()
        #sys.exit(2)
