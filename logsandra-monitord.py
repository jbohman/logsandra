#!/usr/bin/env python
"""
Logsandra monitor daemon
"""
# Global imports
import sys
import os
import optparse
import logging

# Local imports
from logsandra import utils
from logsandra.utils.daemon import Daemon
from logsandra.monitor import config, monitor

class Application(Daemon):

    def run(self):
        logger = logging.getLogger('logsandra.monitord')
        settings = config.parse(self.settings.config_file)
        m = monitor.Monitor(settings, False)
        logger.debug('Starting monitor daemon')
        m.run()


if __name__ == '__main__':

    default_working_directory = os.curdir
    default_config_file = os.path.join(default_working_directory, 'config.yaml')

    usage = 'usage: %prog [options] start|stop|restart'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--config-file', dest='config_file', metavar='FILE', default=default_config_file)
    parser.add_option('--working-directory', dest='working_directory', metavar='DIRECTORY', default=default_working_directory)
    parser.add_option('--pid', dest='pid_file', metavar='FILE', default=os.path.join(default_working_directory, 'logsandra-monitord.pid'))
    parser.add_option('--application-data-directory', dest='application_data_directory', default=utils.application_data_directory('logsandra'))
    (options, args) = parser.parse_args()

    if not os.path.isdir(options.application_data_directory):
        os.makedirs(options.application_data_directory)

    logfile = os.path.join(options.application_data_directory, 'logsandra.log')
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format="%(asctime)s %(levelname)-5.5s [%(name)s] [%(threadName)s] %(message)s")

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
