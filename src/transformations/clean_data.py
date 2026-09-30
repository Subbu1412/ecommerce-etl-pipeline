from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    lower,
    trim,
    when,
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# --------------------------------------------------
# Spark Session
# --------------------------------------------------

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("EcommerceETL-Cleaning")
    .getOrCreate()
)


# --------------------------------------------------
# Create output directory
# --------------------------------------------------

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Read raw data
# --------------------------------------------------

print("\nReading raw datasets...")

customers = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .csv(str(RAW_DIR / "customers.csv"))
)

products = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .csv(str(RAW_DIR / "products.csv"))
)

orders = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .csv(str(RAW_DIR / "orders.csv"))
)

order_items = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .csv(str(RAW_DIR / "order_items.csv"))
)

payments = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .csv(str(RAW_DIR / "payments.csv"))
)


# ==================================================
# CUSTOMERS
# ==================================================

print("\nCleaning customers...")

customers_clean = (
    customers
    # Convert ID to integer
    .withColumn("customer_id", col("customer_id").cast("int"))

    # Clean text fields
    .withColumn("first_name", trim(col("first_name")))
    .withColumn("last_name", trim(col("last_name")))
    .withColumn("city", trim(col("city")))
    .withColumn("state", trim(col("state")))

    # Normalize email
    .withColumn("email", lower(trim(col("email"))))

    # Invalid emails become NULL
    .withColumn(
        "email",
        when(
            col("email").rlike(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
            col("email"),
        ).otherwise(None),
    )

    # Convert signup date
    .withColumn(
        "signup_date",
        col("signup_date").cast("date"),
    )

    # Remove duplicate customer IDs
    .dropDuplicates(["customer_id"])
)


# ==================================================
# PRODUCTS
# ==================================================

print("Cleaning products...")

products_clean = (
    products
    .withColumn("product_id", col("product_id").cast("int"))
    .withColumn("product_name", trim(col("product_name")))
    .withColumn("category", trim(col("category")))
    .withColumn(
        "price",
        col("price").cast("decimal(12,2)"),
    )
)


# ==================================================
# ORDERS
# ==================================================

print("Cleaning orders...")

orders_clean = (
    orders
    .withColumn("order_id", col("order_id").cast("int"))
    .withColumn("customer_id", col("customer_id").cast("int"))
    .withColumn(
        "order_date",
        col("order_date").cast("timestamp"),
    )
    .withColumn("status", trim(col("status")))
)


# ==================================================
# ORDER ITEMS
# ==================================================

print("Cleaning order items...")

order_items_clean = (
    order_items
    .withColumn(
        "order_item_id",
        col("order_item_id").cast("int"),
    )
    .withColumn(
        "order_id",
        col("order_id").cast("int"),
    )
    .withColumn(
        "product_id",
        col("product_id").cast("int"),
    )
    .withColumn(
        "quantity",
        col("quantity").cast("int"),
    )
    .withColumn(
        "unit_price",
        col("unit_price").cast("decimal(12,2)"),
    )

    # Remove invalid quantities
    .filter(col("quantity") > 0)
)


# ==================================================
# PAYMENTS
# ==================================================

print("Cleaning payments...")

payments_clean = (
    payments
    .withColumn(
        "payment_id",
        col("payment_id").cast("int"),
    )
    .withColumn(
        "order_id",
        col("order_id").cast("int"),
    )
    .withColumn(
        "payment_method",
        trim(col("payment_method")),
    )
    .withColumn(
        "payment_status",
        trim(col("payment_status")),
    )
    .withColumn(
        "payment_date",
        col("payment_date").cast("timestamp"),
    )
)


# ==================================================
# Write processed data
# ==================================================

print("\nWriting cleaned Parquet datasets...")

datasets = {
    "customers": customers_clean,
    "products": products_clean,
    "orders": orders_clean,
    "order_items": order_items_clean,
    "payments": payments_clean,
}

for name, dataframe in datasets.items():

    output_path = PROCESSED_DIR / name

    (
        dataframe
        .write
        .mode("overwrite")
        .parquet(str(output_path))
    )

    print(f"Written: {name}")


# ==================================================
# Summary
# ==================================================

print("\n" + "=" * 60)
print("CLEANING SUMMARY")
print("=" * 60)

print(f"Customers:    {customers_clean.count():,}")
print(f"Products:     {products_clean.count():,}")
print(f"Orders:       {orders_clean.count():,}")
print(f"Order Items:  {order_items_clean.count():,}")
print(f"Payments:     {payments_clean.count():,}")

print("\nETL cleaning stage completed successfully!")

spark.stop()