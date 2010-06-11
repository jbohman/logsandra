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
        result = match.groupdict()

        if 'user' in result and result['user'] == '-':
            result['user'] = None

        if 'size' in result and result['size'] == '-':
            result['size'] = None

        if 'size_with_headers' in result and result['size_with_headers'] == '-':
            result['size_with_headers'] = None

        if 'referer' in result and result['referer'] == '-':
            result['referer'] = None

        result['time'] = dateutil.parser.parse(result['time'], fuzzy=True)

        return result
