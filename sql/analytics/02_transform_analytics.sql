-- ============================================================
-- DIMENSION: CUSTOMERS
-- ============================================================

INSERT INTO analytics.dim_customers (
    customer_id,
    first_name,
    last_name,
    email,
    signup_date
)
SELECT
    customer_id,
    first_name,
    last_name,
    email,
    signup_date
FROM staging.customers
ON CONFLICT (customer_id)
DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    signup_date = EXCLUDED.signup_date;


-- ============================================================
-- DIMENSION: PRODUCTS
-- ============================================================

INSERT INTO analytics.dim_products (
    product_id,
    product_name,
    category,
    price
)
SELECT
    product_id,
    product_name,
    category,
    price
FROM staging.products
ON CONFLICT (product_id)
DO UPDATE SET
    product_name = EXCLUDED.product_name,
    category = EXCLUDED.category,
    price = EXCLUDED.price;


-- ============================================================
-- FACT: ORDER ITEMS
-- ============================================================

INSERT INTO analytics.fact_order_items (
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    line_total
)
SELECT
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price AS line_total
FROM staging.order_items
ON CONFLICT (order_item_id)
DO UPDATE SET
    order_id = EXCLUDED.order_id,
    product_id = EXCLUDED.product_id,
    quantity = EXCLUDED.quantity,
    unit_price = EXCLUDED.unit_price,
    line_total = EXCLUDED.line_total;


-- ============================================================
-- FACT: ORDERS
-- ============================================================

INSERT INTO analytics.fact_orders (
    order_id,
    customer_id,
    order_date,
    status,
    total_amount
)
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.status,
    COALESCE(
        SUM(oi.quantity * oi.unit_price),
        0
    ) AS total_amount
FROM staging.orders o
LEFT JOIN staging.order_items oi
    ON o.order_id = oi.order_id
GROUP BY
    o.order_id,
    o.customer_id,
    o.order_date,
    o.status
ON CONFLICT (order_id)
DO UPDATE SET
    customer_id = EXCLUDED.customer_id,
    order_date = EXCLUDED.order_date,
    status = EXCLUDED.status,
    total_amount = EXCLUDED.total_amount;