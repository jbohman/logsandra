import re
import dateutil.parser

from logsandra.monitor.parsers import BaseParser

class SyslogParser(BaseParser):

    def parse(self, line, source, data):
        elements = line.split(' ')


        date = ' '.join(elements[0:3])
        date = dateutil.parser.parse(date, fuzzy=True)

        keywords = []

        host = elements[3]
        keywords.append('host:%s' % host)
        keywords.append(host)

        program = elements[4][0:-1]
        result = re.search(r'(.+)\[([0-9]+)\]', program)
        if result:
            program, pid = result.groups()
            keywords.append('program:%s' % program)
            keywords.append('pid:%s' % pid)
            keywords.append(program)
            keywords.append(pid)
        else:
            keywords.append('program:%s' % program)
            keywords.append(program)

        
        content = elements[5:]
        keywords.append(' '.join(content))
        for c in content:
            keywords.append(c)

        return self.log_entries.add(date=date, entry=line, source=source, keywords=keywords)
