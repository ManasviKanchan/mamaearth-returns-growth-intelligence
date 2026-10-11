
-- Mamaearth Returns & Growth Intelligence Pipeline
-- Part 1: Data loading instructions
-- Run schema.sql before importing CSV files.

-- Import the original CSV files into the corresponding
-- SQLite tables using DB Browser for SQLite:
--
-- data/customers.csv -> customers
-- data/products.csv  -> products
-- data/orders.csv    -> orders
--
-- Preserve NULL values and original payment-method casing.
-- Do not clean or remove duplicate rows in SQL.

-- Verify imported record counts:

SELECT 'Customers' AS table_name, COUNT(*) AS total_rows
FROM customers

UNION ALL

SELECT 'Products', COUNT(*)
FROM products

UNION ALL

SELECT 'Orders', COUNT(*)
FROM orders;
