-- ============================================================
-- DASHBOARD VIEWS
-- ============================================================


-- ============================================================
-- DAILY SALES
-- ============================================================

CREATE OR REPLACE VIEW analytics.v_daily_sales AS
SELECT
    DATE(o.order_date) AS order_date,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.line_total), 2) AS revenue
FROM analytics.fact_orders o
JOIN analytics.fact_order_items oi
    ON o.order_id = oi.order_id
WHERE LOWER(o.status) <> 'cancelled'
GROUP BY DATE(o.order_date)
ORDER BY DATE(o.order_date);


-- ============================================================
-- CATEGORY SALES
-- ============================================================

CREATE OR REPLACE VIEW analytics.v_category_sales AS
SELECT
    p.category,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.line_total), 2) AS revenue
FROM analytics.fact_order_items oi
JOIN analytics.fact_orders o
    ON oi.order_id = o.order_id
JOIN analytics.dim_products p
    ON oi.product_id = p.product_id
WHERE LOWER(o.status) <> 'cancelled'
GROUP BY p.category
ORDER BY revenue DESC;


-- ============================================================
-- PRODUCT SALES
-- ============================================================

CREATE OR REPLACE VIEW analytics.v_product_sales AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.line_total), 2) AS revenue
FROM analytics.fact_order_items oi
JOIN analytics.fact_orders o
    ON oi.order_id = o.order_id
JOIN analytics.dim_products p
    ON oi.product_id = p.product_id
WHERE LOWER(o.status) <> 'cancelled'
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY revenue DESC;