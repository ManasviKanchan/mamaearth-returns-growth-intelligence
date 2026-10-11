
-- Task 3(a): Order Totals
-- Output:
-- total_orders | total_revenue | avg_order_value
-- 180          | 99860.20      | 554.78

SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)
    ), 2) AS total_revenue,
    ROUND(AVG(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)
    ), 2) AS avg_order_value
FROM orders o
JOIN products p
    ON o.product_id = p.product_id;






-- Task 3(b): COUNT(*) vs COUNT(column)
-- Output:
-- total_orders | rated_orders | missing_ratings
-- 180          | 165          | 15

SELECT
    COUNT(*) AS total_orders,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS missing_ratings
FROM orders;





-- Task 3(c): Customers with zero orders
-- Method 1: LEFT JOIN

-- Output:
-- customer_id | name
-- C045        | Vihaan

SELECT
    c.customer_id,
    c.name
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;


-- Task 3(c): Customers with zero orders
-- Method 2: NOT IN

-- Output:
-- customer_id | name
-- C045        | Vihaan

SELECT
    customer_id,
    name
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM orders
);

