import random
import datetime
import time
import struct
import uuid
import pycassa
import math
from cassandra.ttypes import NotFoundException
from ordereddict import OrderedDict

KEYSPACE = 'logsandra'

long_struct = struct.Struct('>q')

def to_long(d, r=None):
    if not r:
        r = random.randrange(999999)
    d = d.replace(microsecond=r)
    return long_struct.pack(int(time.mktime(d.timetuple())) * 1000000 + d.microsecond)

def from_long(l):
    return datetime.datetime.fromtimestamp(long_struct.unpack(l)[0] / 1000000)


class Cassandra(object):

    def __init__(self, ident, host, port, timeout):
        self.ident = ident
        self.client = pycassa.connect(['%s:%s' % (host, port)], timeout=timeout)

        self.cf_entries = pycassa.ColumnFamily(self.client, KEYSPACE, 'entries')
        self.cf_by_date = pycassa.ColumnFamily(self.client, KEYSPACE, 'by_date', dict_class=OrderedDict)
        self.cf_categories = pycassa.ColumnFamily(self.client, KEYSPACE, 'categories', dict_class=OrderedDict)

    def add_entry(self, date, entry, source, keywords):
        if not keywords:
            raise Error('Missing keywords')

        key = uuid.uuid1()
        self.cf_entries.insert(str(key.hex), {'ident': str(self.ident), 'source': source, 'date': date.strftime('%Y-%m-%d %H:%M:%S'), 'entry': str(entry)})

        for keyword in keywords:
            self.cf_by_date.insert(str(keyword), {to_long(date): str(key.hex)})

        return True

    def get_entries_by_keyword(self, keyword, column_start='', column_finish='', column_count=30, action_next=None, action_prev=None):
        if action_next and action_prev:
            raise AttributeError('action_next and action_prev is mutually exclusive')

        column_reversed = False

        if column_start:
            column_start = to_long(column_start, 0)

        if column_finish:
            column_finish = to_long(column_finish, 0)

        if action_next:
            column_start = long_struct.pack(action_next)

        if action_prev:
            if column_start:
                column_finish = column_start
            column_start = long_struct.pack(action_prev)
            column_reversed = True

        try:
            result = self.cf_by_date.get(str(keyword),
                    column_reversed=column_reversed, column_count=column_count+1,
                    column_start=column_start, column_finish=column_finish)
        except NotFoundException:
            return [], None, None

        try:
            entries = self.cf_entries.multiget(result.values())
        except NotFoundException:
            return [], None, None

        loop = result.items()
        if column_reversed:
            loop = reversed(loop)

        values = []
        keys = []
        for k, v in loop:
            if v in entries:
                values.append(entries[v])
                keys.append(k)

        return_next = None
        return_prev = None
        if len(keys) == column_count+1:
            if action_prev:
                values = values[1:]
                return_next = long_struct.unpack(keys[-1])[0] + 1
                return_prev = long_struct.unpack(keys[1])[0] - 1
            elif action_next:
                values = values[0:-1]
                return_next = long_struct.unpack(keys[-2])[0] + 1
                return_prev = long_struct.unpack(keys[0])[0] - 1
            else:
                return_next = long_struct.unpack(keys[-2])[0] + 1
                values = values[0:-1]
        else:
            if action_prev:
                return_next = long_struct.unpack(keys[-1])[0] + 1
            elif action_next:
                return_prev = long_struct.unpack(keys[0])[0] - 1

        return values, return_next, return_prev