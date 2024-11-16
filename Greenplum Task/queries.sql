-- Calculate the total sales amount and the total number of transactions for each month.
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
    DATE_TRUNC('month', st.purchase_date)
ORDER BY
    month_of_transaction;

-- Calculate the 3-month moving average of sales amount for each month. The moving
-- average should be calculated based on the sales data from the previous 3 months
-- (including the current month).
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