import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


def profile_csv(filename):
    path = RAW_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    print("\n" + "=" * 60)
    print(f"FILE: {filename}")
    print("=" * 60)

    print(f"Rows: {len(rows):,}")
    print(f"Columns: {len(reader.fieldnames)}")
    print(f"Columns: {reader.fieldnames}")

    print("\nMissing values:")

    for column in reader.fieldnames:
        missing = sum(
            1
            for row in rows
            if row[column] is None or row[column].strip() == ""
        )

        print(f"  {column}: {missing:,}")


def main():
    files = [
        "customers.csv",
        "products.csv",
        "orders.csv",
        "order_items.csv",
        "payments.csv",
    ]

    for filename in files:
        profile_csv(filename)


if __name__ == "__main__":
    main()