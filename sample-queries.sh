#!/bin/bash
time echo "select count(*) from mydb.test_not_indexed where text like '%ABCDE%'" | curl "http://localhost:8123?allow_experimental_data_skipping_indices=1" -d @-
time echo "select count(*) from mydb.test_indexed where text like '%ABCDE%'" | curl "http://localhost:8123?allow_experimental_data_skipping_indices=1" -d @-
time echo "select count(*) from mydb.test_not_indexed where text like '%sequence:1918%'" | curl "http://localhost:8123?allow_experimental_data_skipping_indices=1" -d @-
time echo "select count(*) from mydb.test_indexed where text like '%sequence:1918%'" | curl "http://localhost:8123?allow_experimental_data_skipping_indices=1" -d @-
