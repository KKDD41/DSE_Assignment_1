# Greenplum Assignment

## Project Structure

- `ddl.sql` contains definitions of schema tables.
- `queries.sql` contains analytical queries required in assignment.
- `./docker_testing/` folder containing files and sources required 
to up and run Greenplum locally. This is still under development.

## Modelling Considerations

### Tables Included

**Customers** table containing details regarding customers. Since it is simple dimensional table,
and likely will be used only within join on `customer_id` with `sales_transactions` table, the following 
constrains were applied:
- Heap table, as customers details like email or address could be modified (frequency unknown + 
could be extanded with more 'dynamic' features like rating, nickname, etc.).
- Primary key and btree-index on `customer_id` field as it would be included in hash-joins frequently.
- Distribution by `customer_id` for even distribution of records between segments.
- Non-generated `customer_id`, assuming it is a business key.
```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(255),
    email_address VARCHAR(255),
    country VARCHAR(100)
) WITH (APPENDONLY=false)
DISTRIBUTED BY (customer_id);
```
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

**Products** table with products list could be assumed as not too large in (terms of rows) and not frequently updated.
In a same way it would be used in join with `sales_transactions` table mostly. Following constrains were applied:
- Primary key on `product_id` field as join-column.
- Heap table, since table is mutable and there is no need for AOT.
- Distributed in a replicated way due to (assumption) small size. That would reduce network overhead during joins.
- Non-generated `product_id`, assuming it is a business key.
```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255),
    price NUMERIC(10,2),
    category VARCHAR(100)
) WITH (APPENDONLY=false)
DISTRIBUTED REPLICATED; 
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

**Sales Transactions** table could be considered as fact table of events (transactions) performed,
which would be used for analysis of sales within certain time period. The following modelling 
approaches were used:
- AOT table, as it would act as append-only fact table.
- Columnar orientation, as analytics would be done on particular set of columns.
- `transaction_id` as generated key of type `SERIAL` with btree index on it (used for joins).
- Distribution by `transaction_id` as it is the most appropriate key for even data distribution (data skew avoiding).
- Partitioning by range with month interval, useful for both analytical queries for particular time-range,
and deletion of old historical data.
```sql
CREATE TABLE sales_transactions (
    transaction_id SERIAL NOT NULL,
    customer_id INTEGER REFERENCES customers(customer_id),
    product_id INTEGER REFERENCES products(product_id),
    purchase_date DATE,
    quantity_purchased INTEGER
) WITH (APPENDONLY=true, orientation=column)
DISTRIBUTED BY (transaction_id)
PARTITION BY RANGE(purchase_date)
(
  PARTITION p1 START('2020-01-01'::DATE) END('2024-01-01'::DATE)
  EVERY('1 month'::INTERVAL),
  DEFAULT PARTITION EXTRA
);
CREATE INDEX sales_transactions_id_idx ON sales_transactions USING btree(transaction_id); 
CREATE INDEX sales_transactions_product_id_idx ON sales_transactions USING btree(product_id); 
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
Indexes:
    "sales_transactions_id_idx" btree (transaction_id)
Foreign-key constraints:
    "sales_transactions_customer_id_fkey" FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    "sales_transactions_product_id_fkey" FOREIGN KEY (product_id) REFERENCES products(product_id)
Child tables: sales_transactions_1_prt_extra,
              sales_transactions_1_prt_p1_1,
              sales_transactions_1_prt_p1_10,
              ...
              sales_transactions_1_prt_p1_7,
              sales_transactions_1_prt_p1_8,
              sales_transactions_1_prt_p1_9
Distributed by: (transaction_id)
Partition by: (purchase_date)
Options: appendonly=true, orientation=column
```

**Shipping Details** table could be also considered as append-only fact table with similar 
structure.
- AOT table, as it would act as append-only fact table.
- Columnar orientation, as analytics would be done on particular set of columns.
- `transaction_id` as non-nullable integer referring to `sales_transactions` table.
- Distribution by `transaction_id` as it is the most appropriate key for even data distribution (data skew avoiding).
- Partitioning by range with month interval, useful for both analytical queries for particular time-range,
and deletion of old historical data.
```sql
CREATE TABLE shipping_details (
    transaction_id INTEGER NOT NULL,
    shipping_date DATE,
    shipping_address VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100)
) WITH (APPENDONLY=true, orientation=column)
DISTRIBUTED BY (transaction_id)
PARTITION BY RANGE(shipping_date)
(
  PARTITION p1 START('2020-01-01'::DATE) END('2024-01-01'::DATE)
  EVERY('1 month'::INTERVAL),
  DEFAULT PARTITION EXTRA
);
CREATE INDEX shipping_details_id_idx ON shipping_details USING btree(transaction_id);
```
```commandline
template1=# \d+ shipping_details
                                               Append-Only Columnar Table "public.shipping_details"
      Column      |          Type          | Modifiers | Storage  | Stats target | Compression Type | Compression Level | Block Size | Description 
------------------+------------------------+-----------+----------+--------------+------------------+-------------------+------------+-------------
 transaction_id   | integer                | not null  | plain    |              | none             | 0                 | 32768      | 
 shipping_date    | date                   |           | plain    |              | none             | 0                 | 32768      | 
 shipping_address | character varying(255) |           | extended |              | none             | 0                 | 32768      | 
 city             | character varying(100) |           | extended |              | none             | 0                 | 32768      | 
 country          | character varying(100) |           | extended |              | none             | 0                 | 32768      | 
Checksum: t
Indexes:
    "shipping_details_id_idx" btree (transaction_id)
Child tables: shipping_details_1_prt_extra,
              shipping_details_1_prt_p1_1,
              shipping_details_1_prt_p1_10,
              ...
              shipping_details_1_prt_p1_7,
              shipping_details_1_prt_p1_8,
              shipping_details_1_prt_p1_9
Distributed by: (transaction_id)
Partition by: (shipping_date)
Options: appendonly=true, orientation=column
```

Here I did not cover compression applying, however it also could be a point of further improvement.

## Queries Explanation

### Sales amount and transactions count per month

### SQL Query
Calculate the total sales amount and the total number of transactions for each month.
```sql
SELECT
    DATE_TRUNC('month', st.purchase_date) AS month_of_transaction,
    COUNT(st.transaction_id) AS total_transactions,
    SUM(p.price * st.quantity_purchased) AS total_sales_amount
FROM
    sales_transactions st
JOIN
    products p
        ON st.product_id = p.product_id
GROUP BY
    DATE_TRUNC('month', st.purchase_date);
```

### Query Plan
```commandline
                                                                            QUERY PLAN                                                                            
------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Gather Motion 1:1  (slice2; segments: 1)  (cost=0.00..437.00 rows=1 width=24) (actual time=5.089..5.089 rows=0 loops=1)
   ->  GroupAggregate  (cost=0.00..437.00 rows=1 width=24) (never executed)
         Group Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
         ->  Sort  (cost=0.00..437.00 rows=1 width=24) (never executed)
               Sort Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
               Sort Method:  quicksort  Memory: 33kB
               ->  Result  (cost=0.00..437.00 rows=1 width=24) (never executed)
                     // TODO: Achive hash-join instead
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
 Planning time: 18.329 ms
   (slice0)    Executor memory: 168K bytes.
   (slice1)    Executor memory: 1756K bytes (seg0).
   (slice2)    Executor memory: 160K bytes (seg0).  Work_mem: 33K bytes max.
 Memory used:  128000kB
```

### Moving-average of sales amount within 3 months interval

#### SQL Query
 Calculate the 3-month moving average of sales amount for each month. The moving
 average should be calculated based on the sales data from the previous 3 months
 (including the current month).
```sql
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', st.purchase_date) AS month_of_transaction,
        SUM(p.price * st.quantity_purchased) AS total_sales
    FROM
        sales_transactions st
    JOIN
        products p
            ON st.product_id = p.product_id
    GROUP BY
        DATE_TRUNC('month', st.purchase_date)
)
SELECT
    ms.month_of_transaction,
    ms.total_sales,
    AVG(ms.total_sales) OVER (ORDER BY ms.month_of_transaction ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS three_month_moving_avg
FROM
    monthly_sales ms
ORDER BY
    ms.month_of_transaction;
```

#### Query Plan
```commandline
                                                                                        QUERY PLAN

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------
 Sort  (cost=0.00..437.00 rows=1 width=24) (actual time=7.748..7.748 rows=0 loops=1)
   Sort Key: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
   Sort Method:  quicksort  Memory: 33kB
   ->  WindowAgg  (cost=0.00..437.00 rows=1 width=24) (actual time=7.732..7.732 rows=0 loops=1)
         Order By: (date_trunc('month'::text, (sales_transactions.purchase_date)::timestamp with time zone))
         ->  Gather Motion 1:1  (slice2; segments: 1)  (cost=0.00..437.00 rows=1 width=16) (actual time=7.731..7.731 rows=0 loops=1)
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
                                             // TODO: Acheive hash-join instead
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
 Planning time: 42.906 ms
   (slice0)    Executor memory: 324K bytes.  Work_mem: 33K bytes max.
   (slice1)    Executor memory: 1660K bytes (seg0).
   (slice2)    Executor memory: 220K bytes (seg0).  Work_mem: 33K bytes max.
 Memory used:  128000kB
 Optimizer: Pivotal Optimizer (GPORCA)
 Execution time: 14.254 ms
```

## Additional Notes

1. Seems that initial tables design (commit: `b4da2fe`) produces not optimized query plans with broadcast motion overhead
and wrong type of join methods (two indexed fields are joined by nested loop instead hash join). 
Approach as always worked fine in theory, however on practice Greenplum still chooses Nested Loop :).
2. Later, will populate tables with rows and rerun queries. Unfortunately, quite huge time was spent to just start Greenplum locally.
3. Foreign Keys constraints have no effect in Greenplum, however they have been added to DDL as a reminder,
that they probably could be enforced by triggers ON INSERT / ON UPDATE (but only in case of a big desire).