import re
import dateutil.parser

clf = {
    '%h': r'(?P<host>\S+)',
    '%l': r'\S+',
    '%u': r'(?P<user>\S+)',
    '%t': r'\[(?P<time>.+)\]', 
    '%r': r'"(?P<request>.+)"',   
    '%s': r'(?P<status>[0-9]+)',
    '%>s': r'(?P<status>[0-9]+)',
    '%<s': r'(?P<status>[0-9]+)',
    '%b': r'(?P<size>\S+)',
    '%O': r'(?P<size_with_headers>\S+)',
    '%{Referer}i': r'"(?P<referer>.*)"',
    '%{User-Agent}i': r'"(?P<user_agent>.*)"',
    '%U': r'(?P<url_path>\S+)',
    '%p': r'(?P<port>[0-9]+)',
    '%v': r'(?P<server>\S+)'
}

class ClfParser(object):

    def __init__(self, format):
        self.format = format

        parts = []
        for element in self.format.split(' '):
            parts.append(clf[element])

        self.pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')

    def parse_line(self, line):
        match = self.pattern.match(line)
        res = match.groupdict()

        if 'user' in res and res['user'] == '-':
            res['user'] = None

        if 'size' in res and res['size'] == '-':
            res['size'] = None

        if 'size_with_headers' in res and res['size_with_headers'] == '-':
            res['size_with_headers'] = None

        if 'referer' in res and res['referer'] == '-':
            res['referer'] = None

        res['time'] = dateutil.parser.parse(res['time'], fuzzy=True)

        return res
