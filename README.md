# clickhouse-example

Run `./clickhouse-index-example.py` to generate two tables, each containing 100M of records with random strings in `text` field

Run `./sample-queries.sh` to run several queries that are supposed to use indexing

Sample output (ingestion was in progress so results do not match exactly):

```
$ time echo "select count(*) from mydb.test_not_indexed where text like '%ABCDE%'" | curl "http://localhost:8123?allow_experimental_data_skipping_indices=1" -d @-
125

real	0m18.051s
user	0m0.000s
sys	0m0.004s

$ time echo "select count(*) from mydb.test_indexed where text like '%ABCDE%'" | curl "http://localhost:8123?allow_experimental_data_skipping_indices=1" -d @-
126

real	0m14.859s
user	0m0.000s
sys	0m0.004s

$ time echo "select count(*) from mydb.test_not_indexed where text like '%sequence:1918%'" | curl "http://localhost:8123?allow_experimental_data_skipping_indices=1" -d @-
4057

real	0m14.148s
user	0m0.004s
sys	0m0.000s

$ time echo "select count(*) from mydb.test_indexed where text like '%sequence:1918%'" | curl "http://localhost:8123?allow_experimental_data_skipping_indices=1" -d @-
4087

real	0m14.703s
user	0m0.000s
sys	0m0.004s
```
