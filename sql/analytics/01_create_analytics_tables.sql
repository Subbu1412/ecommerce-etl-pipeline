CREATE TABLE IF NOT EXISTS analytics.dim_customers (
    customer_id      INTEGER PRIMARY KEY,
    first_name       VARCHAR(100),
    last_name        VARCHAR(100),
    email            VARCHAR(255),
    signup_date      DATE
);

CREATE TABLE IF NOT EXISTS analytics.dim_products (
    product_id       INTEGER PRIMARY KEY,
    product_name     VARCHAR(255),
    category         VARCHAR(100),
    price            NUMERIC(12, 2)
);

CREATE TABLE IF NOT EXISTS analytics.fact_orders (
    order_id         INTEGER PRIMARY KEY,
    customer_id      INTEGER,
    order_date       TIMESTAMP,
    status           VARCHAR(50),
    total_amount     NUMERIC(12, 2)
);

CREATE TABLE IF NOT EXISTS analytics.fact_order_items (
    order_item_id    INTEGER PRIMARY KEY,
    order_id         INTEGER,
    product_id       INTEGER,
    quantity         INTEGER,
    unit_price       NUMERIC(12, 2),
    line_total       NUMERIC(12, 2)
);