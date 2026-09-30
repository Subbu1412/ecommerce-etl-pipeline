from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    when,
    trim,
    lower,
)


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


def main():

    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName("EcommerceDataQuality")
        .getOrCreate()
    )

    # -----------------------------
    # Load raw datasets
    # -----------------------------

    customers = spark.read.option("header", True).csv(
        str(RAW_DIR / "customers.csv")
    )

    products = spark.read.option("header", True).csv(
        str(RAW_DIR / "products.csv")
    )

    orders = spark.read.option("header", True).csv(
        str(RAW_DIR / "orders.csv")
    )

    order_items = spark.read.option("header", True).csv(
        str(RAW_DIR / "order_items.csv")
    )

    payments = spark.read.option("header", True).csv(
        str(RAW_DIR / "payments.csv")
    )

    # -----------------------------
    # Customers
    # -----------------------------

    print("\n" + "=" * 60)
    print("CUSTOMER DATA QUALITY")
    print("=" * 60)

    print("\nDuplicate customer IDs:")

    (
        customers
        .groupBy("customer_id")
        .count()
        .filter(col("count") > 1)
        .show()
    )

    print("\nMissing emails:")

    customers.filter(
        col("email").isNull() | (trim(col("email")) == "")
    ).show()

    print("\nInvalid email format:")

    customers.filter(
        ~lower(col("email")).rlike(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    ).show()

    # -----------------------------
    # Order Items
    # -----------------------------

    print("\n" + "=" * 60)
    print("ORDER ITEM DATA QUALITY")
    print("=" * 60)

    print("\nInvalid quantities:")

    order_items.filter(
        col("quantity").cast("int") <= 0
    ).show()

    print("\nInvalid prices:")

    order_items.filter(
        col("unit_price").cast("double") <= 0
    ).show()

    # -----------------------------
    # Referential Integrity
    # -----------------------------

    print("\n" + "=" * 60)
    print("REFERENTIAL INTEGRITY")
    print("=" * 60)

    print("\nOrders with missing customers:")

    (
        orders.alias("o")
        .join(
            customers.alias("c"),
            col("o.customer_id") == col("c.customer_id"),
            "left_anti",
        )
        .show()
    )

    print("\nOrder items with missing orders:")

    (
        order_items.alias("oi")
        .join(
            orders.alias("o"),
            col("oi.order_id") == col("o.order_id"),
            "left_anti",
        )
        .show()
    )

    print("\nOrder items with missing products:")

    (
        order_items.alias("oi")
        .join(
            products.alias("p"),
            col("oi.product_id") == col("p.product_id"),
            "left_anti",
        )
        .show()
    )

    # -----------------------------
    # Payment Analysis
    # -----------------------------

    print("\n" + "=" * 60)
    print("PAYMENT ANALYSIS")
    print("=" * 60)

    print("\nPayment status distribution:")

    payments.groupBy("payment_status").count().show()

    print("\nOrders without payments:")

    (
        orders.alias("o")
        .join(
            payments.alias("p"),
            col("o.order_id") == col("p.order_id"),
            "left_anti",
        )
        .show()
    )

    spark.stop()


if __name__ == "__main__":
    main()