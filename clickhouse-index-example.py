#!/usr/bin/env python3
from clickhouse_driver import Client
import time
import random
import string

db_name = "mydb"
table_name_base = "test7"
desired_records = 100000000
package_size = 10000

client = Client('localhost')
client.execute('SET allow_experimental_data_skipping_indices=1')
client.execute('CREATE DATABASE IF NOT EXISTS {}'.format(db_name))

def table_name(with_index):
    if with_index:
        return table_name_base+"_indexed"
    else:
        return table_name_base+"_not_indexed"

def create_table(with_index):
    if with_index:
#        index_definition = ', INDEX text_index1 text TYPE ngrambf_v1(3, 24576, 8, 0) GRANULARITY 1, INDEX text_index2 text TYPE ngrambf_v1(4, 98304, 5, 0) GRANULARITY 8, INDEX text_index3 text TYPE ngrambf_v1(5, 98304, 5, 0) GRANULARITY 128'
        index_definition = ', INDEX text_index2 text TYPE ngrambf_v1(4, 131072, 5, 0) GRANULARITY 2, INDEX text_index3 text TYPE ngrambf_v1(5, 4194304, 4, 0) GRANULARITY 64'
    else:
        index_definition = ''

    client.execute('CREATE TABLE IF NOT EXISTS {}.{}('
               '  _date Date DEFAULT today() CODEC(LZ4),'
               '  time_stamp_ms Int64 CODEC(LZ4),'
               '  id Int64 CODEC(LZ4),'
               '  text String CODEC(LZ4)'
               '  {}'
               ') ENGINE = MergeTree'
               ' PARTITION BY (_date)'
               ' ORDER BY (time_stamp_ms)'
               ' SETTINGS index_granularity = 512'
               .format(db_name, table_name(with_index), index_definition))
               
def random_sequence(len):
    xx = []
    for i in range(len):
        xx.append(random.choice(string.ascii_uppercase + string.digits + ' '))
    return "".join(xx)


create_table(True)
create_table(False)


records_count = 0
total_duration = {"indexed": 0.0, "not_indexed": 0.0}

while records_count < desired_records:
    insert_sets = []
    
    columns = ["id", "time_stamp_ms", "text"]
    
    for i in range(package_size):
        insert = {
            "id": random.randint(100000,10000000000), 
            "time_stamp_ms":int(time.time()*1000), 
            "text": random_sequence(random.randint(10,400)) + ' sequence:{}'.format(i)
        }
        
        insert_sets.append(insert)
        
    t0 = time.time()
    client.execute(
        'INSERT INTO {}.{} ({}) VALUES'.format(db_name, table_name(True), ",".join(columns))
        ,insert_sets)
    t1 = time.time()

    client.execute(
        'INSERT INTO {}.{} ({}) VALUES'.format(db_name, table_name(False), ",".join(columns))
        ,insert_sets)
    t2 = time.time()
    
    records_count += len(insert_sets)
    
    total_duration['indexed'] += (t1-t0)
    total_duration['not_indexed'] += (t2-t1)
    print("Set of {} records inserted in {} seconds (INDEXED) / {} seconds (NOT INDEXED). In total, {} records inserted with average of {} records/s (INDEXED) / {} records/s (NOT INDEXED)".format(
        len(insert_sets), (t1-t0), (t2-t1), records_count, records_count/total_duration['indexed'], records_count/total_duration['not_indexed']
    ))
