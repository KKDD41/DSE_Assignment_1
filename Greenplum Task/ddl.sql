DROP TABLE shipping_details;
DROP TABLE sales_transactions;
DROP TABLE products;
DROP TABLE customers;

-- Customers Table
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(255),
    email_address VARCHAR(255),
    country VARCHAR(100)
) WITH (APPENDONLY=false)
DISTRIBUTED BY (customer_id);

-- Products Table
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255),
    price NUMERIC(10,2),
    category VARCHAR(100)
) WITH (APPENDONLY=false)
DISTRIBUTED REPLICATED;

-- Sales Transactions Table
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

-- Shipping Details Table
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