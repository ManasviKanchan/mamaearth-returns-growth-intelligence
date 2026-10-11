
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



-- Task 3(d): City-wise Return Rate Analysis
-- Output:
-- city      | total_orders | returned_orders | return_rate_pct
-- Jaipur    | 19           | 8               | 42.1
-- Lucknow   | 49           | 15              | 30.6
-- Bangalore | 33           | 8               | 24.2

SELECT
    c.city,
    COUNT(*) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND(100.0 * SUM(o.returned) / COUNT(*), 1)
        AS return_rate_pct
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;



-- ==========================================
-- Task 3(e): Customer Spending Rankings
-- ==========================================

-- Query 1: Top 5 Customers by Total Spending
-- Output:
-- customer_id | name    | total_spend
-- C043        | Reyansh | 12920.00
-- C026        | Isha    | 8371.60
-- C008        | Meera   | 4564.60
-- C011        | Arjun   | 4111.00
-- C042        | Sanya   | 3785.00

-- customer_id ASC ensures consistent ranking
-- when customers have the same total spending.

SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)
    ), 2) AS total_spend
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;


-- Query 2: Customers Ranked 3 to 5
-- Output:
-- customer_id | name  | total_spend
-- C008        | Meera | 4564.60
-- C011        | Arjun | 4111.00
-- C042        | Sanya | 3785.00

SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)
    ), 2) AS total_spend
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;



-- ==========================================
-- Task 3(f): Category-wise Revenue Analysis
-- ==========================================

-- Output:
-- category     | order_count | category_revenue
-- Haircare     | 54          | 44956.10
-- Skincare     | 60          | 27346.00
-- Babycare     | 30          | 16805.00
-- PersonalCare | 36          | 10753.10

SELECT
    p.category,
    COUNT(*) AS order_count,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)
    ), 2) AS category_revenue
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;



-- ==========================================
-- Task 3(g): LIKE Pattern Matching
-- ==========================================

-- Output:
-- customer_id | name
-- C001        | Aarav
-- C003        | Aditi
-- C004        | Ananya
-- C011        | Arjun
-- C021        | Aryan
-- C030        | Anika
-- C031        | Aditya
-- C036        | Aisha
-- C041        | Ayaan
-- C044        | Aria

SELECT
    customer_id,
    name
FROM customers
WHERE name LIKE 'A%'
ORDER BY customer_id;



-- ==========================================
-- Task 3(h): DISTINCT Acquisition Sources
-- ==========================================

-- Output:
-- acquisition_source
-- Ad
-- Organic
-- Referral
-- Social

SELECT DISTINCT
    acquisition_source
FROM customers
ORDER BY acquisition_source;



-- ==========================================
-- Task 3(i): ALTER TABLE + CASE
-- ==========================================

-- Step 1: Add loyalty_tier column
ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

-- Step 2: Assign loyalty tiers
UPDATE customers
SET loyalty_tier =
    CASE
        WHEN city_tier = 1 THEN 'Gold'
        ELSE 'Silver'
    END;

-- Step 3: Verify loyalty tier distribution
-- Output:
-- loyalty_tier | customer_count
-- Gold         | 28
-- Silver       | 17

SELECT
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;
