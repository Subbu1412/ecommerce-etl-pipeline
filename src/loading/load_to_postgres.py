from pathlib import Path
import os

import psycopg2
from psycopg2.extras import execute_values

from pyspark.sql import SparkSession


BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
    "database": os.getenv("PGDATABASE", "ecommerce"),
    "user": os.getenv("PGUSER", "etl_user"),
    "password": os.getenv("PGPASSWORD", "etl_password"),
}


TABLES = {
    "customers": [
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "signup_date",
    ],
    "products": [
        "product_id",
        "product_name",
        "category",
        "price",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "order_date",
        "status",
    ],
    "order_items": [
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
    ],
    "payments": [
        "payment_id",
        "order_id",
        "payment_method",
        "payment_status",
        "payment_date",
    ],
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def load_table(spark, conn, table_name, columns):
    parquet_path = str(PROCESSED_DIR / table_name)

    print(f"\nLoading {table_name}...")
    print(f"Reading Parquet: {parquet_path}")

    # Read Spark-generated Parquet using Spark itself.
    df = spark.read.parquet(parquet_path)

    # Select only the PostgreSQL columns we need.
    df = df.select(*columns)

    # Collect because our synthetic datasets are small.
    rows = [
        tuple(row[column] for column in columns)
        for row in df.collect()
    ]

    if not rows:
        print(f"{table_name}: no rows found")
        return

    column_list = ", ".join(columns)

    sql = f"""
        INSERT INTO staging.{table_name} ({column_list})
        VALUES %s
        ON CONFLICT DO NOTHING
    """

    with conn.cursor() as cursor:
        execute_values(
            cursor,
            sql,
            rows,
            page_size=1000,
        )

    conn.commit()

    print(f"{table_name}: {len(rows):,} rows loaded")


def main():

    print("=" * 60)
    print("PARQUET → POSTGRESQL LOADING")
    print("=" * 60)

    spark = (
        SparkSession.builder
        .appName("EcommerceParquetToPostgres")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    conn = get_connection()

    try:

        print("\nClearing staging tables...")

        with conn.cursor() as cursor:
            cursor.execute("""
                TRUNCATE TABLE
                    staging.order_items,
                    staging.payments,
                    staging.orders,
                    staging.products,
                    staging.customers;
            """)

        conn.commit()

        for table_name, columns in TABLES.items():
            load_table(
                spark,
                conn,
                table_name,
                columns,
            )

        print("\n" + "=" * 60)
        print("LOADING COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:

        conn.rollback()

        print("\nLoading failed:")
        print(e)

        raise

    finally:

        conn.close()

        spark.stop()


if __name__ == "__main__":
    main()