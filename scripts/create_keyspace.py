#!/usr/bin/env python
from thrift import Thrift
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol.TBinaryProtocol import TBinaryProtocolAccelerated
from cassandra import Cassandra
from cassandra.ttypes import *

KEYSPACE_NAME = 'logsandra'

class CassandraClientHelper(Cassandra.Client, object):

    def __init__(self, host, port):
        self._socket = TSocket.TSocket(host, port)
        self._transport = TTransport.TBufferedTransport(self._socket)
        self._protocol = TBinaryProtocol.TBinaryProtocolAccelerated(self._transport)
        super(CassandraClientHelper, self).__init__(self._protocol)

    def __enter__(self):
        self._transport.open()

    def __exit__(self, exc_type, exc_value, traceback):
        self._transport.close()

if __name__ == '__main__':

    # Keyspace
    logsandra = KsDef(name=KEYSPACE_NAME, strategy_class='org.apache.cassandra.locator.RackUnawareStrategy', replication_factor=1, cf_defs=[])

    # Column families
    entries = CfDef(table=KEYSPACE_NAME, name='entries', column_type='Standard', clock_type='Timestamp', comparator_type='BytesType', 
                        reconciler='', comment='', row_cache_size=0, preload_row_cache=False, key_cache_size=200000)
    by_date = CfDef(table=KEYSPACE_NAME, name='by_date', column_type='Standard', clock_type='Timestamp', comparator_type='LongType', 
                        reconciler='', comment='', row_cache_size=0, preload_row_cache=False, key_cache_size=200000)
    column_families = {'entries': entries, 'by_date': by_date}

    # Connect to a Cassandra node
    client = CassandraClientHelper('localhost', 9160)
    with client:
        # Describe keyspaces
        try:
            keyspaces = client.describe_keyspaces()
        except Thrift.TException, tx:
            print 'Thrift: %s' % tx.message

        # If keyspace do not exists, add it
        if KEYSPACE_NAME not in keyspaces:
            try: 
                result = client.system_add_keyspace(logsandra)
                print 'Added keyspace: %s [%s]' % (KEYSPACE_NAME, result)
            except Thrift.TException, tx:
                print 'Thrift: %s' % tx.message
        else:
            print 'Keyspace %s, already added' % (KEYSPACE_NAME)

       
        # Set keyspace
        client.set_keyspace(KEYSPACE_NAME)

        # Describe keyspace
        try:
            keyspace = client.describe_keyspace(KEYSPACE_NAME)
        except Thrift.TException, tx:
            print 'Thrift: %s' % tx.message

        # Add column families
        for key, value in column_families.iteritems():
            if key not in keyspace:
                try: 
                    result = client.system_add_column_family(value)
                    print 'Added column family: %s [%s]' % (key, result)
                except Thrift.TException, tx:
                    print 'Thrift: %s' % tx.message
                except InvalidRequestException, e:
                    print 'Cassandra: %s' % e
            else:
                print 'Column family %s, already added' % (key)

