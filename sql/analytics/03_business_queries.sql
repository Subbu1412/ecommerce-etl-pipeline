-- 1. Total revenue
SELECT
    ROUND(SUM(total_amount), 2) AS total_revenue
FROM analytics.fact_orders
WHERE status <> 'cancelled';


-- 2. Average order value
SELECT
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM analytics.fact_orders
WHERE status <> 'cancelled';


-- 3. Revenue by category
SELECT
    p.category,
    ROUND(SUM(oi.line_total), 2) AS revenue
FROM analytics.fact_order_items oi
JOIN analytics.dim_products p
    ON oi.product_id = p.product_id
JOIN analytics.fact_orders o
    ON oi.order_id = o.order_id
WHERE o.status <> 'cancelled'
GROUP BY p.category
ORDER BY revenue DESC;


-- 4. Top 10 products by revenue
SELECT
    p.product_id,
    p.product_name,
    ROUND(SUM(oi.line_total), 2) AS revenue
FROM analytics.fact_order_items oi
JOIN analytics.dim_products p
    ON oi.product_id = p.product_id
JOIN analytics.fact_orders o
    ON oi.order_id = o.order_id
WHERE o.status <> 'cancelled'
GROUP BY
    p.product_id,
    p.product_name
ORDER BY revenue DESC
LIMIT 10;


-- 5. Top 10 customers by spending
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    ROUND(SUM(o.total_amount), 2) AS total_spent
FROM analytics.fact_orders o
JOIN analytics.dim_customers c
    ON o.customer_id = c.customer_id
WHERE o.status <> 'cancelled'
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name
ORDER BY total_spent DESC
LIMIT 10;


-- 6. Daily revenue
SELECT
    DATE(order_date) AS order_day,
    ROUND(SUM(total_amount), 2) AS revenue
FROM analytics.fact_orders
WHERE status <> 'cancelled'
GROUP BY DATE(order_date)
ORDER BY order_day;


-- 7. Order status distribution
SELECT
    status,
    COUNT(*) AS order_count
FROM analytics.fact_orders
GROUP BY status
ORDER BY order_count DESC;


-- 8. Payment success rate
SELECT
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE payment_status = 'Success'
        ) / COUNT(*),
        2
    ) AS payment_success_rate
FROM staging.payments;