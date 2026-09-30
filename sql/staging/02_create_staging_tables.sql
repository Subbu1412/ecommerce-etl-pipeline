CREATE TABLE IF NOT EXISTS staging.customers (
    customer_id      INTEGER PRIMARY KEY,
    first_name       VARCHAR(100),
    last_name        VARCHAR(100),
    email            VARCHAR(255),
    signup_date      DATE
);

CREATE TABLE IF NOT EXISTS staging.products (
    product_id       INTEGER PRIMARY KEY,
    product_name     VARCHAR(255),
    category         VARCHAR(100),
    price            NUMERIC(12, 2)
);

CREATE TABLE IF NOT EXISTS staging.orders (
    order_id         INTEGER PRIMARY KEY,
    customer_id      INTEGER,
    order_date       TIMESTAMP,
    status            VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS staging.order_items (
    order_item_id    INTEGER PRIMARY KEY,
    order_id         INTEGER,
    product_id       INTEGER,
    quantity         INTEGER,
    unit_price       NUMERIC(12, 2)
);

CREATE TABLE IF NOT EXISTS staging.payments (
    payment_id       INTEGER PRIMARY KEY,
    order_id         INTEGER,
    payment_method   VARCHAR(50),
    payment_status   VARCHAR(50),
    payment_date     TIMESTAMP
);