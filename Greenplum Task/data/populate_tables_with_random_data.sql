INSERT INTO customers (customer_id, customer_name, email_address, country)
SELECT
    s,
    'Customer ' || s,
    md5(random()::text) || '@example.com',
    CASE WHEN s % 3 = 0 THEN 'USA'
         WHEN s % 3 = 1 THEN 'Canada'
         ELSE 'Mexico'
    END
FROM generate_series(1, 5000) s;  -- Generates 5000 customers


INSERT INTO products (product_id, product_name, price, category)
SELECT
    s,
    'Product ' || s,
    (random() * 100)::numeric(10,2),
    CASE WHEN s % 4 = 0 THEN 'Electronics'
         WHEN s % 4 = 1 THEN 'Books'
         WHEN s % 4 = 2 THEN 'Clothing'
         ELSE 'Household'
    END
FROM generate_series(1, 500) s;  -- Generates 500 products


INSERT INTO sales_transactions (customer_id, product_id, purchase_date, quantity_purchased)
SELECT
    (random() * 4999 + 1)::integer,  -- Random customer_id between 1 and 5000
    (random() * 499 + 1)::integer,  -- Random product_id between 1 and 500
    timestamp '2020-01-01' + random() * (timestamp '2023-12-31' - timestamp '2020-01-01'),  -- Random date between 2020 and 2023
    (random() * 10 + 1)::integer  -- Random quantity between 1 and 10
FROM generate_series(1, 10000) s;  -- Generates 10000 transactions


INSERT INTO shipping_details (transaction_id, shipping_date, shipping_address, city, country)
SELECT
    transaction_id,
    purchase_date + (random() * 10)::integer,  -- Shipping date is within 10 days after purchase
    'Address ' || md5(random()::text),
    CASE WHEN (random() * 3)::integer = 0 THEN 'CityA'
         WHEN (random() * 3)::integer = 1 THEN 'CityB'
         ELSE 'CityC'
    END,
    CASE WHEN (random() * 3)::integer = 0 THEN 'CountryA'
         WHEN (random() * 3)::integer = 1 THEN 'CountryB'
         ELSE 'CountryC'
    END
FROM sales_transactions;