# Greenplum Assignment

## Project Structure

- `ddl.sql` contains definitions of schema tables.
- `queries.sql` contains analytical queries required in assignment.
- `./docker_testing/` folder containing files and sources required 
to up and run Greenplum locally. This is still under development.

## Modelling Considerations

### Tables Included
```commandline

template1=# \d+ customers
                                  Table "public.customers"
    Column     |          Type          | Modifiers | Storage  | Stats target | Description
---------------+------------------------+-----------+----------+--------------+-------------
 customer_id   | integer                | not null  | plain    |              |
 customer_name | character varying(255) |           | extended |              |
 email_address | character varying(255) |           | extended |              |
 country       | character varying(100) |           | extended |              |
Indexes:
    "customers_pkey" PRIMARY KEY, btree (customer_id)
Distributed by: (customer_id)
Options: appendonly=false
```

```commandline
template1=# \d+ products
                                  Table "public.products"
    Column    |          Type          | Modifiers | Storage  | Stats target | Description
--------------+------------------------+-----------+----------+--------------+-------------
 product_id   | integer                | not null  | plain    |              |
 product_name | character varying(255) |           | extended |              |
 price        | numeric(10,2)          |           | main     |              |
 category     | character varying(100) |           | extended |              |
Indexes:
    "products_pkey" PRIMARY KEY, btree (product_id)
Distributed Replicated
Options: appendonly=false
```

```commandline
template1=# \d+ sales_transactions
                                                                        Append-Only Columnar Table "public.sales_transactions"
       Column       |  Type   |                                  Modifiers                                  | Storage | Stats target | Compression Type | Compression Level | Block 
Size | Description 
--------------------+---------+-----------------------------------------------------------------------------+---------+--------------+------------------+-------------------+-------
-----+-------------
 transaction_id     | integer | not null default nextval('sales_transactions_transaction_id_seq'::regclass) | plain   |              | none             | 0                 | 32768 
     | 
 customer_id        | integer |                                                                             | plain   |              | none             | 0                 | 32768 
     | 
 product_id         | integer |                                                                             | plain   |              | none             | 0                 | 32768 
     | 
 purchase_date      | date    |                                                                             | plain   |              | none             | 0                 | 32768 
     | 
 quantity_purchased | integer |                                                                             | plain   |              | none             | 0                 | 32768 
     |
Checksum: t
Foreign-key constraints:
    "sales_transactions_customer_id_fkey" FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    "sales_transactions_product_id_fkey" FOREIGN KEY (product_id) REFERENCES products(product_id)
Child tables: sales_transactions_1_prt_extra,
              sales_transactions_1_prt_p1_1,
              sales_transactions_1_prt_p1_10,
              sales_transactions_1_prt_p1_11,
              sales_transactions_1_prt_p1_12,
              sales_transactions_1_prt_p1_13,
              sales_transactions_1_prt_p1_14,
              sales_transactions_1_prt_p1_15,
              sales_transactions_1_prt_p1_16,
              sales_transactions_1_prt_p1_17,
              sales_transactions_1_prt_p1_18,
              sales_transactions_1_prt_p1_19,
              sales_transactions_1_prt_p1_2,
              sales_transactions_1_prt_p1_20,
              sales_transactions_1_prt_p1_21,
              sales_transactions_1_prt_p1_22,
              sales_transactions_1_prt_p1_23,
              sales_transactions_1_prt_p1_24,
              sales_transactions_1_prt_p1_25,
              sales_transactions_1_prt_p1_26,
              sales_transactions_1_prt_p1_27,
              sales_transactions_1_prt_p1_28,
              sales_transactions_1_prt_p1_29,
              sales_transactions_1_prt_p1_3,
              sales_transactions_1_prt_p1_30,
              sales_transactions_1_prt_p1_31,
              sales_transactions_1_prt_p1_32,
              sales_transactions_1_prt_p1_33,
              sales_transactions_1_prt_p1_34,
              sales_transactions_1_prt_p1_35,
              sales_transactions_1_prt_p1_36,
              sales_transactions_1_prt_p1_37,
              sales_transactions_1_prt_p1_38,
              sales_transactions_1_prt_p1_39,
              sales_transactions_1_prt_p1_4,
              sales_transactions_1_prt_p1_40,
              sales_transactions_1_prt_p1_41,
              sales_transactions_1_prt_p1_42,
              sales_transactions_1_prt_p1_43,
              sales_transactions_1_prt_p1_44,
              sales_transactions_1_prt_p1_45,
              sales_transactions_1_prt_p1_46,
              sales_transactions_1_prt_p1_47,
              sales_transactions_1_prt_p1_48,
              sales_transactions_1_prt_p1_5,
              sales_transactions_1_prt_p1_6,
              sales_transactions_1_prt_p1_7,
              sales_transactions_1_prt_p1_8,
              sales_transactions_1_prt_p1_9
Distributed by: (transaction_id)
Partition by: (purchase_date)
Options: appendonly=true, orientation=column
```

```commandline
template1=# \d+ shipping_details;
                                               Append-Only Columnar Table "public.shipping_details"
      Column      |          Type          | Modifiers | Storage  | Stats target | Compression Type | Compression Level | Block Size | Description
------------------+------------------------+-----------+----------+--------------+------------------+-------------------+------------+-------------
 transaction_id   | integer                | not null  | plain    |              | none             | 0                 | 32768      |
 shipping_date    | date                   |           | plain    |              | none             | 0                 | 32768      |
 shipping_address | character varying(255) |           | extended |              | none             | 0                 | 32768      |
 city             | character varying(100) |           | extended |              | none             | 0                 | 32768      |
 country          | character varying(100) |           | extended |              | none             | 0                 | 32768      |
Checksum: t
Child tables: shipping_details_1_prt_extra,
              shipping_details_1_prt_p1_1,
              shipping_details_1_prt_p1_10,
              shipping_details_1_prt_p1_11,
              shipping_details_1_prt_p1_12,
              shipping_details_1_prt_p1_13,
              shipping_details_1_prt_p1_14,
              shipping_details_1_prt_p1_15,
              shipping_details_1_prt_p1_16,
              shipping_details_1_prt_p1_17,
              shipping_details_1_prt_p1_18,
              shipping_details_1_prt_p1_19,
              shipping_details_1_prt_p1_2,
              shipping_details_1_prt_p1_20,
              shipping_details_1_prt_p1_21,
              shipping_details_1_prt_p1_22,
              shipping_details_1_prt_p1_23,
              shipping_details_1_prt_p1_24,
              shipping_details_1_prt_p1_25,
              shipping_details_1_prt_p1_26,
              shipping_details_1_prt_p1_27,
              shipping_details_1_prt_p1_28,
              shipping_details_1_prt_p1_29,
              shipping_details_1_prt_p1_3,
              shipping_details_1_prt_p1_30,
              shipping_details_1_prt_p1_31,
              shipping_details_1_prt_p1_32,
              shipping_details_1_prt_p1_33,
              shipping_details_1_prt_p1_34,
              shipping_details_1_prt_p1_35,
              shipping_details_1_prt_p1_36,
              shipping_details_1_prt_p1_37,
              shipping_details_1_prt_p1_38,
              shipping_details_1_prt_p1_39,
              shipping_details_1_prt_p1_4,
              shipping_details_1_prt_p1_40,
              shipping_details_1_prt_p1_41,
              shipping_details_1_prt_p1_42,
              shipping_details_1_prt_p1_43,
              shipping_details_1_prt_p1_44,
              shipping_details_1_prt_p1_45,
              shipping_details_1_prt_p1_46,
              shipping_details_1_prt_p1_47,
              shipping_details_1_prt_p1_48,
              shipping_details_1_prt_p1_5,
              shipping_details_1_prt_p1_6,
              shipping_details_1_prt_p1_7,
              shipping_details_1_prt_p1_8,
              shipping_details_1_prt_p1_9
Distributed by: (transaction_id)
Partition by: (shipping_date)
Options: appendonly=true, orientation=column
```

### Distribution

### Partitioning

### Compression

## Queries Explanation

### Sales amount and transactions count per month
```commandline
                                                                               QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Gather Motion 1:1  (slice2; segments: 1)  (cost=0.00..437.00 rows=1 width=24) (actual time=9.917..9.917 rows=0 loops=1)
   Merge Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
   ->  Sort  (cost=0.00..437.00 rows=1 width=24) (never executed)
         Sort Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
         Sort Method:  quicksort  Memory: 33kB
         ->  GroupAggregate  (cost=0.00..437.00 rows=1 width=24) (never executed)
               Group Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
               ->  Sort  (cost=0.00..437.00 rows=1 width=24) (never executed)
                     Sort Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
                     Sort Method:  quicksort  Memory: 33kB
                     ->  Result  (cost=0.00..437.00 rows=1 width=24) (never executed)
                           ->  Nested Loop  (cost=0.00..437.00 rows=1 width=20) (never executed)
                                 Join Filter: true
                                 ->  Broadcast Motion 1:1  (slice1; segments: 1)  (cost=0.00..431.00 rows=1 width=16) (never executed)
                                       ->  Sequence  (cost=0.00..431.00 rows=1 width=16) (never executed)
                                             ->  Partition Selector for sales_transactions (dynamic scan id: 1)  (cost=10.00..100.00 rows=100 width=4) (never executed)
                                                   Partitions selected: 49 (out of 49)
                                             ->  Dynamic Seq Scan on sales_transactions (dynamic scan id: 1)  (cost=0.00..431.00 rows=1 width=16) (never executed)
                                                   Partitions scanned:  49 (out of 49) .
                                 ->  Index Scan using products_pkey on products  (cost=0.00..6.00 rows=1 width=8) (never executed)
                                       Index Cond: (product_id = sales_transactions.product_id)
 Planning time: 35.383 ms
```

### Moving-average of sales amount within 3 months interval
```commandline
                                                                                        QUERY PLAN
      
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------
 Sort  (cost=0.00..437.00 rows=1 width=24) (actual time=7.106..7.106 rows=0 loops=1)
   Sort Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
   Sort Method:  quicksort  Memory: 33kB
   ->  WindowAgg  (cost=0.00..437.00 rows=1 width=24) (actual time=7.092..7.092 rows=0 loops=1)
         Order By: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
         ->  Gather Motion 1:1  (slice2; segments: 1)  (cost=0.00..437.00 rows=1 width=16) (actual time=7.089..7.089 rows=0 loops=1)
               Merge Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
               ->  Result  (cost=0.00..437.00 rows=1 width=16) (never executed)
                     ->  Sort  (cost=0.00..437.00 rows=1 width=16) (never executed)
                           Sort Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
                           Sort Method:  quicksort  Memory: 33kB
                           ->  GroupAggregate  (cost=0.00..437.00 rows=1 width=16) (never executed)
                                 Group Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
                                 ->  Sort  (cost=0.00..437.00 rows=1 width=20) (never executed)
                                       Sort Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
                                       Sort Method:  quicksort  Memory: 33kB
                                       ->  Result  (cost=0.00..437.00 rows=1 width=20) (never executed)
                                             ->  Nested Loop  (cost=0.00..437.00 rows=1 width=16) (never executed)
                                                   Join Filter: true
                                                   ->  Broadcast Motion 1:1  (slice1; segments: 1)  (cost=0.00..431.00 rows=1 width=12) (never executed)
                                                         ->  Sequence  (cost=0.00..431.00 rows=1 width=12) (never executed)
                                                               ->  Partition Selector for sales_transactions (dynamic scan id: 1)  (cost=10.00..100.00 rows=100 width=4) (never exec
uted)
                                                                     Partitions selected: 49 (out of 49)
                                                               ->  Dynamic Seq Scan on sales_transactions (dynamic scan id: 1)  (cost=0.00..431.00 rows=1 width=12) (never executed)
                                                                     Partitions scanned:  49 (out of 49) .
                                                   ->  Index Scan using products_pkey on products  (cost=0.00..6.00 rows=1 width=8) (never executed)
                                                         Index Cond: (product_id = sales_transactions.product_id)
 Planning time: 17.480 ms
```


## Additional Notes
