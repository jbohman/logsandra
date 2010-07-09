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

    def __init__(self, log_entries):
        self.log_entries = log_entries

    def parse(self, line, data):
        print data
        parts = []
        for element in data['clf_format'].split(' '):
            parts.append(clf[element])

        # TODO: optimize by storing compiled regex?
        pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')
        match = pattern.match(line)
        result = match.groupdict()

        keywords = []

        if 'user' in result and result['user'] != '-':
            keywords.append('user:%s' % result['user'])
            keywords.append(result['user'])

        if 'user_agent' in result and result['user_agent'] != '-':
            keywords.append('user_agent:%s' % result['user_agent'])
            keywords.append(result['user_agent'])
           
        if 'referer' in result and result['referer'] != '-':
            keywords.append('referer:%s' % result['referer'])
            keywords.append(result['referer'])

        if 'request' in result and result['request'] != '-':
            request_parts = result['request'].split(' ')
            keywords.extend(request_parts)
            keywords.append('request_type:%s' % request_parts[0])
            keywords.append('request_url:%s' % request_parts[1])
            keywords.append('request:%s' % result['request'])
            keywords.append(result['request'])

        if 'status' in result and result['status'] != '-':
            keywords.append('status_code:%s' % result['status'])
            keywords.append(result['status'])

        if 'host' in result and result['host'] != '-':
            keywords.append('host:%s' % result['host'])
            keywords.append(result['host'])

        if 'port' in result and result['port'] != '-':
            keywords.append('port:%s' % result['port'])
            keywords.append(result['port'])

        if 'server' in result and result['server'] != '-':
            keywords.append('server:%s' % result['server'])
            keywords.append(result['server'])

        date = dateutil.parser.parse(result['time'], fuzzy=True).replace(tzinfo=None)

        return self.log_entries.add(date, line, data['source'], keywords)
