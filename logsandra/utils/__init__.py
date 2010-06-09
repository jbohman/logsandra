import sys
import os

def application_data_directory(appname):
    if sys.platform == 'darwin':
        from AppKit import NSSearchPathForDirectoriesInDomains
        appdata = path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], appname)
    elif sys.platform == 'win32':
        appdata = os.path.join(os.environ['APPDATA'], appname)
    else:
        appdata = os.path.expanduser(os.path.join("~", "." + appname))
    return appdata
