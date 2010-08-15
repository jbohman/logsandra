#!/usr/bin/env python
from thrift import Thrift
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol.TBinaryProtocol import TBinaryProtocolAccelerated
from cassandra import Cassandra
from cassandra.ttypes import *

KEYSPACE = 'logsandra'

class CassandraClientHelper(Cassandra.Client, object):

    def __init__(self, host, port):
        self._socket = TSocket.TSocket(host, port)
        self._transport = TTransport.TFramedTransport(self._socket)
        self._protocol = TBinaryProtocol.TBinaryProtocolAccelerated(self._transport)
        super(CassandraClientHelper, self).__init__(self._protocol)

    def __enter__(self):
        self._transport.open()

    def __exit__(self, exc_type, exc_value, traceback):
        self._transport.close()

if __name__ == '__main__':

    # Keyspace
    logsandra = KsDef(name=KEYSPACE, strategy_class='org.apache.cassandra.locator.SimpleStrategy', replication_factor=1, cf_defs=[])

    # Column families
    column_families = {
        'entries': CfDef(keyspace=KEYSPACE, name='entries', column_type='Standard', clock_type='Timestamp', comparator_type='BytesType',
                        reconciler='', comment='', row_cache_size=0, preload_row_cache=False, key_cache_size=200000),
        'by_date': CfDef(keyspace=KEYSPACE, name='by_date', column_type='Standard', clock_type='Timestamp', comparator_type='LongType',
                        reconciler='', comment='', row_cache_size=0, preload_row_cache=False, key_cache_size=200000),
        'by_date_data': CfDef(keyspace=KEYSPACE, name='by_date_data', column_type='Standard', clock_type='Timestamp', comparator_type='LongType',
                        reconciler='', comment='', row_cache_size=0, preload_row_cache=False, key_cache_size=200000),
        'categories': CfDef(keyspace=KEYSPACE, name='categories', column_type='Standard', clock_type='Timestamp', comparator_type='UTF8Type',
                        reconciler='', comment='', row_cache_size=0, preload_row_cache=False, key_cache_size=200000)
    }

    # Connect to a Cassandra node
    client = CassandraClientHelper('localhost', 9160)
    with client:

        # Describe keyspaces
        keyspaces = client.describe_keyspaces()
        keyspace_names = [keyspace.name for keyspace in keyspaces]
        
        # If keyspace do not exists, add it
        if KEYSPACE not in keyspace_names:
            result = client.system_add_keyspace(logsandra)
            print 'Added keyspace: %s [%s]' % (KEYSPACE, result)
        else:
            print 'Keyspace %s, already added' % (KEYSPACE)

        # Set keyspace and describe it
        client.set_keyspace(KEYSPACE)
        keyspace = client.describe_keyspace(KEYSPACE)
        keyspace_cf_names = [cf.name for cf in keyspace.cf_defs]

        # Add column families
        for key, value in column_families.iteritems():
            if key not in keyspace_cf_names:
                result = client.system_add_column_family(value)
                print 'Added column family: %s [%s]' % (key, result)
            else:
                print 'Column family %s, already added' % (key)

