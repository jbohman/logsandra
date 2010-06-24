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

    def get_entries_by_keyword(self, keyword, column_start=None, column_finish=None, column_count=30, action_next=None):
        if action_next:
            column_start = long_struct.pack(action_next)
        elif column_start:
            column_start = to_long(column_start)

        try:
            if column_start and not column_finish:
                result = self.cf_by_date.get(str(keyword), column_count=column_count, column_start=column_start)
            elif column_start and column_finish:
                result = self.cf_by_date.get(str(keyword), column_count=column_count, column_start=column_start, column_finish=to_long(column_finish, 0))
            else:
                result = self.cf_by_date.get(str(keyword), column_count=column_count)
        except NotFoundException:
            return [], None

        try:
            entries = self.cf_entries.multiget(result.values())
        except NotFoundException:
            return [], None

        return_value = []
        return_next = None
        for k, v in result.items():
            if v in entries:
                return_value.append(entries[v])
                return_next = k
        
        return return_value, long_struct.unpack(return_next)[0] + 1


    """
    def get_entries_by_keyword(self, keyword, column_start=None, column_finish=None, column_count=10, action_next=None, action_prev=None, prev=[]):
        if action_next and action_prev:
            raise AttributeError('action_next and action_prev is mutually exclusive')

        column_reversed = False
        if not column_start and not column_finish:
            if action_next:
                column_start = long_struct.pack(action_next)

            if action_prev:
                column_start = long_struct.pack(action_prev[-2])

        try:
            if column_start and not column_finish:
                result = self.cf_by_date.get(str(keyword),
                        column_count=column_count,
                        column_reversed=column_reversed,
                        column_start=column_start)
            elif column_start and column_finish:
                result = self.cf_by_date.get(str(keyword),
                        column_count=column_count,
                        column_reversed=column_reversed,
                        column_start=column_start,
                        column_finish=column_finish)
            else:
                result = self.cf_by_date.get(str(keyword),
                        column_count=column_count,
                        column_reversed=column_reversed)
        except NotFoundException:
            return OrderedDict(), None

        try:
            entries = self.cf_entries.multiget(result.values())
        except NotFoundException:
            return OrderedDict(), None

        return_value = OrderedDict()
        return_next = None
        return_prev = None
        for k, v in result.items():
            if v in entries:
                if not return_prev:
                    return_prev = k
                return_value[v] = entries[v]
                return_next = k

        if action_prev:
            prev.pop()
        else:
            prev.append(long_struct.unpack(return_prev)[0])

        return return_value, (long_struct.unpack(return_next)[0] + 1), prev
    """

