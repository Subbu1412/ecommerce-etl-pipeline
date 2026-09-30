from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def generate_data():
    import subprocess

    result = subprocess.run(
        [
            "python",
            "/opt/airflow/src/generate_data.py",
        ],
        capture_output=True,
        text=True,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Data generation failed")


def clean_data():
    import subprocess

    result = subprocess.run(
        [
            "python",
            "/opt/airflow/src/transformations/clean_data.py",
        ],
        capture_output=True,
        text=True,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("PySpark cleaning failed")


def load_to_postgres():
    import os
    import subprocess

    env = os.environ.copy()

    env["PGHOST"] = "host.docker.internal"
    env["PGPORT"] = "5432"
    env["PGDATABASE"] = "ecommerce"
    env["PGUSER"] = "etl_user"
    env["PGPASSWORD"] = "etl_password"

    result = subprocess.run(
        [
            "python",
            "/opt/airflow/src/loading/load_to_postgres.py",
        ],
        capture_output=True,
        text=True,
        env=env,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("PostgreSQL loading failed")


def transform_analytics():
    import os
    import psycopg2

    sql_path = "/opt/airflow/sql/analytics/02_transform_analytics.sql"

    with open(sql_path, "r", encoding="utf-8") as file:
        sql = file.read()

    conn = psycopg2.connect(
        host="host.docker.internal",
        port=5432,
        database="ecommerce",
        user="etl_user",
        password="etl_password",
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)

        conn.commit()

        print("Analytics transformations completed successfully!")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def create_dashboard_views():
    import psycopg2

    sql_path = "/opt/airflow/sql/analytics/04_dashboard_views.sql"

    with open(sql_path, "r", encoding="utf-8") as file:
        sql = file.read()

    conn = psycopg2.connect(
        host="host.docker.internal",
        port=5432,
        database="ecommerce",
        user="etl_user",
        password="etl_password",
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)

        conn.commit()

        print("Dashboard views created successfully!")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


with DAG(
    dag_id="ecommerce_etl",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["ecommerce", "etl", "pyspark", "postgres"],
) as dag:

    generate = PythonOperator(
        task_id="generate_data",
        python_callable=generate_data,
    )

    clean = PythonOperator(
        task_id="clean_data_with_pyspark",
        python_callable=clean_data,
    )

    load = PythonOperator(
        task_id="load_parquet_to_postgres",
        python_callable=load_to_postgres,
    )

    transform = PythonOperator(
        task_id="transform_analytics",
        python_callable=transform_analytics,
    )

    dashboard_views = PythonOperator(
        task_id="create_dashboard_views",
        python_callable=create_dashboard_views,
    )

    generate >> clean >> load >> transform >> dashboard_views