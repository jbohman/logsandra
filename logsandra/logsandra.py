# Global imports
import sys
import os
import optparse
import time

# Local imports
import config
from utils.daemon import Daemon


class Application(Daemon):

    # TODO: setup application here, monitor + pylon webservice
    def run(self):
        while 1:
            time.sleep(10)


if __name__ == '__main__':

    default_working_directory = os.curdir
    default_path = os.path.split(os.path.dirname(__file__))[0]
    default_config_file = os.path.join(default_path, 'config.yaml')

    usage = 'usage: %prog [options] start|stop|restart'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--config-file', dest='config_file', metavar='FILE', default=default_config_file)
    parser.add_option('--working-directory', dest='working_directory', metavar='DIRECTORY', default=default_working_directory)
    parser.add_option('--pid-file', dest='pid_file', metavar='FILE', default='/tmp/logsandra.pid')
    (options, args) = parser.parse_args()

    settings = config.parse(options.config_file)
    application = Application(options.pid_file)
    application.settings = settings

    if len(args) == 1:
        if args[0] == 'start':
            application.start()
        elif args[0] == 'stop':
            application.stop()
        elif args[0] == 'restart':
            application.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        
        sys.exit(0)
    else:
        print parser.get_usage()
        sys.exit(2)
